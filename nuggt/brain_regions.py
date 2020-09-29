"""Parser for Allen Brain Atlas structures.csv file

"""

import csv
import json
import sys
from urllib.request import urlopen

URL = "http://api.brain-map.org/api/v2/structure_graph_download/1.json"


def make_brain_regions_file(dest):
    with urlopen(URL) as fd:
        download = json.load(fd)
    records = []
    do_level(0, download["msg"], records, -1)
    with open(dest, "w") as fd:
        fd.write(",".join([BrainRegions.ID_FIELD_NAME,
                           BrainRegions.NAME_FIELD_NAME,
                           BrainRegions.ACRONYM_FIELD_NAME,
                           BrainRegions.PARENT_STRUCTURE_ID_FIELD_NAME,
                           BrainRegions.DEPTH_FIELD_NAME]))
        fd.write("\n")
        for record in records:
            fd.write('%d,"%s","%s",%d,%d\n' % (
                record[BrainRegions.ID_FIELD_NAME],
                record[BrainRegions.NAME_FIELD_NAME],
                record[BrainRegions.ACRONYM_FIELD_NAME],
                record[BrainRegions.PARENT_STRUCTURE_ID_FIELD_NAME],
                record[BrainRegions.DEPTH_FIELD_NAME]
            ))


def do_level(level, items, records, parent):
    for d in items:
        idx = len(records)
        acronym = d["acronym"]
        if "name" in d:
            name = d["name"]
        else:
            name = acronym
        record = dict(id=idx, name=name, acronym=acronym,
                      parent_structure_id=parent,
                      depth=level)
        records.append(record)
        do_level(level+1, d["children"], records, parent=idx)


class BrainRegions:
    ID_FIELD_NAME = "id"
    NAME_FIELD_NAME = "name"
    ACRONYM_FIELD_NAME = "acronym"
    PARENT_STRUCTURE_ID_FIELD_NAME = "parent_structure_id"
    DEPTH_FIELD_NAME = "depth"


    @staticmethod
    def parse(fd):
        """Parse a BrainRegions structure from an open file handle

        :param fd: a file opened in "r" mode or file-like object
        """
        rdr = csv.reader(fd)
        header = next(rdr)
        lines = list(rdr)
        return BrainRegions(header, lines)

    def __init__(self, header, lines):
        """Constructor

        :param header: the header line of the file.
        :param lines: the body of the brain regions file, composed of rows
        of fields. The field type is given by the header. Fields past the
        header's length are the hierarchy of brain regions
        """
        id_idx = header.index(self.ID_FIELD_NAME)
        name_idx = header.index(self.NAME_FIELD_NAME)
        acronym_idx = header.index(self.ACRONYM_FIELD_NAME)
        parent_idx = header.index(self.PARENT_STRUCTURE_ID_FIELD_NAME)
        level_idx = header.index(self.DEPTH_FIELD_NAME)

        self.id_per_region = {}
        self.name_per_id = {}
        self.acronym_per_id = {}
        self.id_per_acronym = {}
        self.id_per_region = {}
        self.level_per_id = {}
        self.parent_per_id = {}
        self.level_per_id = {}
        self.id_level = {}

        for line in lines:
            if len(line) == 0:
                continue
            fields = line
            idd = int(fields[id_idx])
            name = fields[name_idx]
            acronym = fields[acronym_idx]
            try:
                parent_id = int(fields[parent_idx])
            except ValueError:
                parent_id = 0
            level = int(fields[level_idx])
            self.name_per_id[idd] = name
            self.acronym_per_id[idd] = acronym
            self.id_per_acronym[acronym] = idd
            self.name_per_id[idd] = name
            self.id_level[idd] = level
            if parent_id != -1:
                self.parent_per_id[idd] = parent_id
            if name not in self.id_per_region:
                self.id_per_region[name] = set()
            self.id_per_region[name].add(idd)
            self.level_per_id[idd] = { level:idd }
        for idd, parent in self.parent_per_id.items():
            d = self.level_per_id[idd]
            idd_base = idd
            while idd in self.parent_per_id:
                idd = self.parent_per_id[idd]
                d[self.id_level[idd]] = idd
                self.id_per_region[self.name_per_id[idd]].add(idd_base)

    def get_name(self, idx):
        """Return the name of a brain region, given the segmentation ID

        :param idx: the ID of the brain region, e.g. from a reference
        segmentation.
        :returns: the name associated with that ID
        """
        return self.name_per_id[idx]

    def get_level_name(self, idx, level):
        """Return the name of the level (1 to 7) for a given ID

        :param idx: the ID of the brain region
        :param level: the level, from 1 (the most gross level) to 7 (the most
        fine)
        """
        try:
            idd = self.level_per_id[idx][level]
        except KeyError:
            return 'id_{}'.format(idx)
        return self.name_per_id[idd]

    def get_acronym(self, idx):
        """Return the acronym / abbreviation for a segmentation ID

        :param idx: the ID of the brain region
        :returns: the acronym / abbreviation for the brain region
        """
        return self.acronym_per_id[idx]

    def get_acronym_id(self, acronym):
        """
        Return the ID for a given acronym
        :param acronym:
        :return:
        """
        return self.id_per_acronym[acronym]

    def get_hierarchy(self, idx):
        """Return the hierchy of brain regions for a given ID

        :param idx: The segmentation ID in question
        :returns: A list, from most specific to least specific of the
        names of brain regions containing the brain region for this ID
        (including the name that maps to the ID)
        """
        names = [ self.get_name(idx) ]
        while idx in self.parent_per_id:
            idx = self.parent_per_id[idx]
            names.append(self.get_name(idx))
        return names

    def get_ids_for_region(self, name):
        """Given a region name, get the IDs of all segments in that region

        :param name: The name of a region, e.g. "Brain stem"
        :returns: a list of all IDs whose corresponding region is either
        the named region or a subregion thereof.
        """
        return self.id_per_region.get(name, [])


def main():
    make_brain_regions_file(sys.argv[1])


if __name__ == "__main__":
    main()
