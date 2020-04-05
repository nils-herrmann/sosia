from os.path import expanduser

URL_CONTENT = "https://www.elsevier.com/solutions/scopus/how-scopus-works/content"
URL_SOURCES = "https://elsevier.com/?a=734751"

FIELDS_SOURCES_LIST = expanduser("~/.sosia/") + "field_sources_list.csv"
SOURCES_NAMES_LIST = expanduser("~/.sosia/") + "sources_names.csv"
CONFIG_FILE = expanduser("~/.sosia/config.ini")

CACHE_TABLES = {
    "author_cits_size":
        {"columns": (("auth_id", "int"), ("year", "int"), ("n_cits", "int")),
         "primary": ("auth_id", "year")},
    "author_size":
        {"columns": (("auth_id", "int"), ("year", "int"), ("n_pubs", "int")),
         "primary": ("auth_id", "year")},
    "author_year":
        {"columns": (("auth_id", "int"), ("year", "int"), ("first_year", "int"),
                     ("n_pubs", "int"), ("n_coauth", "int")),
         "primary": ("auth_id", "year")},
    "authors":
        {"columns": (("auth_id", "int"), ("eid", "text"), ("surname", "text"),
                     ("initials", "text"), ("givenname", "text"),
                     ("affiliation", "text"), ("documents", "text"),
                     ("affiliation_id", "text"), ("city", "text"),
                     ("country", "text"), ("areas", "text")),
         "primary": ("auth_id",)},
    "sources":
        {"columns": (("source_id", "int"), ("year", "int"), ("auids", "text")),
         "primary": ("source_id", "year")},
    "sources_afids":
        {"columns": (("source_id", "int"), ("year", "int"), ("afid", "int"),
                     ("auids", "text")),
         "primary": ("source_id", "year", "afid")}}