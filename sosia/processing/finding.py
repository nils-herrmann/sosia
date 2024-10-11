"""Module with functions for finding matches within a search group based on various criteria
such as publications, citations, coauthors, and affiliations.
"""

from itertools import product

import pandas as pd

from sosia.processing.getting import get_author_data, get_author_info, \
    get_authors_from_sourceyear, get_citations
from sosia.processing.utils import flat_set_from_df, margin_range
from sosia.utils import custom_print


def find_matches(original, verbose, refresh):
    """Find matches within the search group.

    Parameters
    ----------
    original : sosia.Original()
        The object containing information for the original scientist to
        search for.  Attribute search_group needs to exist.

    verbose : bool (optional, default=False)
        Whether to report on the progress of the process.

    refresh : bool, int (optional, default=False)
        Whether to refresh cached results (if they exist) or not, with
        Scopus data that is at most `refrsh` days old (True = 0).
    """
    # Variables
    _years = (original.first_year-original.first_year_margin,
              original.first_year+original.first_year_margin)
    _npapers = margin_range(len(original.publications), original.pub_margin)
    _ncits = margin_range(original.citations, original.cits_margin)
    _ncoauth = margin_range(len(original.coauthors), original.coauth_margin)
    text = f"Filtering {len(original.search_group):,} candidates..."
    custom_print(text, verbose)
    conn = original.sql_conn

    # First round of filtering: minimum publications and main field
    info = get_author_info(original.search_group, original.sql_conn,
                           verbose=verbose, refresh=refresh)
    same_field = info['areas'].str.startswith(original.main_field[1])
    info = info[same_field]
    text = (f"... left with {info.shape[0]:,} candidates in main "
            f"field ({original.main_field[1]})")
    custom_print(text, verbose)
    enough_pubs = info['documents'].astype(int) >= int(min(_npapers))
    info = info[enough_pubs]
    text = (f"... left with {info.shape[0]:,} candidates with sufficient total "
            f"publications ({min(_npapers):,})")
    custom_print(text, verbose)

    # Second round of filtering: first year, publication count, coauthor count
    data = get_author_data(group=sorted(info["auth_id"].unique()),
                           verbose=verbose, conn=conn, refresh=refresh)
    similar_start = data["first_year"].between(_years[0], _years[1])
    data = data[similar_start].drop(columns="first_year")
    data = data[data["year"] <= original.match_year]
    data = data.drop_duplicates("auth_id", keep="last")
    text = (f"... left with {data.shape[0]:,} candidates with similar "
            f"year of first publication ({_years[0]} to {_years[1]})")
    custom_print(text, verbose)
    similar_pubcount = data["n_pubs"].between(min(_npapers), max(_npapers))
    data = data[similar_pubcount]
    text = (f"... left with {data.shape[0]:,} candidates with similar "
            f"number of publications ({min(_npapers):,} to {max(_npapers):,})")
    custom_print(text, verbose)
    similar_coauthcount = data["n_coauth"].between(min(_ncoauth), max(_ncoauth))
    data = data[similar_coauthcount]
    text = (f"... left with {data.shape[0]:,} candidates with similar "
            f"number of coauthors ({min(_ncoauth):,} to {max(_ncoauth):,})")
    custom_print(text, verbose)

    # Third round of filtering: citations
    citations = get_citations(sorted(data["auth_id"].unique()), original.year,
                              verbose=verbose, conn=conn)
    similar_citcount = citations["n_cits"].between(min(_ncits), max(_ncits))
    citations = citations[similar_citcount]
    text = (f"... left with {citations.shape[0]:,} candidates with similar "
            f"number of citations ({min(_ncits):,} to {max(_ncits):,})")
    custom_print(text, verbose)
    group = sorted(citations['auth_id'].unique())

    # Fourth round of filtering: affiliations
    if original.search_affiliations:
        text = "Filtering based on affiliations..."
        custom_print(text, verbose)
        group[:] = [m for m in group if same_affiliation(original, m, refresh)]
        text = (f"... left with {len(group):,} candidates from same "
                f"affiliation ({'-'.join(original.affiliation_id)})")
        custom_print(text, verbose)

    return group


def same_affiliation(original, new, refresh=False):
    """Whether a new scientist shares affiliation(s) with the
    original scientist.
    """
    from sosia.classes import Scientist

    m = Scientist([new], original.year, refresh=refresh,
                  db_path=original.sql_fname)
    return any(str(a) in m.affiliation_id for a in original.search_affiliations)


def search_group_from_sources(original, stacked=False, verbose=False,
                              refresh=False):
    """Define groups of authors based on publications from a set of sources.

    Parameters
    ----------
    original : sosia.Original
        The object of the Scientist to search information for.

    stacked : bool (optional, default=False)
        Whether to use fewer queries that are not reusable, or to use modular
        queries of the form "SOURCE-ID(<SID>) AND PUBYEAR IS <YYYY>".

    verbose : bool (optional, default=False)
        Whether to report on the progress of the process.

    refresh : bool (optional, default=False)
        Whether to refresh cached search files.

    Returns
    -------
    group : set
        Set of authors publishing in year of treatment, in years around
        first publication, and not before them.
    """
    # Define variables
    search_sources, _ = zip(*original.search_sources)
    text = f"Defining 'search_group' using up to {len(search_sources):,} sources..."
    custom_print(text, verbose)

    # Retrieve author list for today
    sources_today = pd.DataFrame(product(search_sources, [original.active_year]),
                                 columns=["source_id", "year"])
    auth_today = get_authors_from_sourceyear(sources_today, original.sql_conn,
        refresh=refresh, stacked=stacked, verbose=verbose)
    if original.search_affiliations:
        same_affs = auth_today["afid"].isin(original.search_affiliations)
        auth_today = auth_today[same_affs]
    today = flat_set_from_df(auth_today, "auids")

    # Authors active around year of first publication
    min_year = original.first_year - original.first_year_margin
    max_year = original.first_year + original.first_year_margin
    then_years = list(range(min_year, max_year+1))
    sources_then = pd.DataFrame(product(search_sources, then_years),
                                columns=["source_id", "year"])
    auth_then = get_authors_from_sourceyear(sources_then, original.sql_conn,
        refresh=refresh, stacked=stacked, verbose=verbose)
    then = flat_set_from_df(auth_then, "auids")

    # Remove authors active before
    sources_before = pd.DataFrame(product(search_sources, [min_year - 1]),
                                  columns=["source_id", "year"])
    auth_before = get_authors_from_sourceyear(sources_before, original.sql_conn,
                                              refresh=refresh, stacked=stacked,
                                              verbose=verbose)
    before = flat_set_from_df(auth_before, "auids")
    then -= before

    # Compile group
    group = today.intersection(then)
    return {int(a) for a in group}
