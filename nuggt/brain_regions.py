"""Parser for Allen Brain Atlas all_brain_regions.csv file


The structure of the file is:
header line
body lines

with each body line composed of integer, float or string fields.
A string field starts with "b'" and ends with "'".
A float field has a period in it and can be parsed using float()
An integer field is anything else.
"""

import csv


class BrainRegions:

    ID_FIELD_NAME = "id"
    COUNTS_FIELD_NAME = "counts"
    DENSITY_FIELD_NAME = "density"
    NAME_FIELD_NAME = "name"
    ACRONYM_FIELD_NAME = "acronym"

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
        counts_idx = header.index(self.COUNTS_FIELD_NAME)
        density_idx = header.index(self.DENSITY_FIELD_NAME)
        name_idx = header.index(self.NAME_FIELD_NAME)
        acronym_idx = header.index(self.ACRONYM_FIELD_NAME)
        hierarchy_idx = len(header)

        self.counts_per_id = {}
        self.densities_per_id = {}
        self.id_per_name = {}
        self.name_per_id = {}
        self.acronym_per_id = {}
        self.hierarchy = {}
        self.id_per_region = {}
        self.level_per_id = {}

        for line in lines:
            idd, counts, density, name, acronym = [
                line[idx][2:-1] if line[idx].startswith("b")
                else float(line[idx]) if "." in line[idx]
                else int(line[idx])
                for idx in
                (id_idx, counts_idx, density_idx, name_idx, acronym_idx)
            ]
            self.id_per_name[name] = idd
            self.name_per_id[idd] = name
            self.counts_per_id[idd] = counts
            self.densities_per_id[idd] = density
            self.acronym_per_id[idd] = acronym
            self.name_per_id[idd] = name
            if name not in self.id_per_region:
                self.id_per_region[name] = set()
            self.id_per_region[name].add(idd)
            prev = name
            self.level_per_id[idd] = []
            for nxt in line[hierarchy_idx:]:
                self.level_per_id[idd].insert(0, nxt[2:-1])
                nxt = nxt[2:-1]
                if nxt != prev:
                    self.hierarchy[prev] = nxt
                    prev = nxt
                    if nxt not in self.id_per_region:
                        self.id_per_region[nxt] = set()
                    self.id_per_region[nxt].add(idd)

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
            name = self.level_per_id[idx][level - 1 ]
        except KeyError:
            name = 'id_{}'.format(idx)
        return name

    def get_acronym(self, idx):
        """Return the acronym / abbreviation for a segmentation ID

        :param idx: the ID of the brain region
        :returns: the acronym / abbreviation for the brain region
        """
        return self.acronym_per_id[idx]

    def get_hierarchy(self, idx):
        """Return the hierchy of brain regions for a given ID

        :param idx: The segmentation ID in question
        :returns: A list, from most specific to least specific of the
        names of brain regions containing the brain region for this ID
        (including the name that maps to the ID)
        """
        names = [ self.get_name(idx) ]
        while names[-1] in self.hierarchy:
            names.append(self.hierarchy[names[-1]])
        return names

    def get_ids_for_region(self, name):
        """Given a region name, get the IDs of all segments in that region

        :param name: The name of a region, e.g. "Brain stem"
        :returns: a list of all IDs whose corresponding region is either
        the named region or a subregion thereof.
        """
        return self.id_per_region.get(name, [])
