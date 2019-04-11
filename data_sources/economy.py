import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

current_date = datetime.date.today()


class NetCompensation():
    default_year = ((current_date.year - 2)
                    if current_date.month < 10
                    else current_date.year - 1)

    """ Distribution of wage earners by level of net compensation """
    url_frmt = "https://www.ssa.gov/cgi-bin/netcomp.cgi?year={year}"

    @staticmethod
    def clean_element(td):
        s = td.text.strip()
        clean_s = s.replace(",", "").replace("$", "")
        clean_s = clean_s.split("—")[0].split("and")[0].strip()
        try:
            return float(clean_s)
        except ValueError:
            return s

    @staticmethod
    def get(year=default_year, **_):
        """
        Args:
            year (int): year of the data to load

        Returns:
            pd.DataFrame
        """
        url = NetCompensation.url_frmt.format(year=year)
        with urlopen(url) as webobj:
            soup = BeautifulSoup(webobj.read(), "html.parser")

        data_tables = soup.find_all('table', attrs=dict(border="1"))
        dist_table = data_tables[1]
        headers = [
            th.text
            for th in dist_table.find_all('th', attrs=dict(scope="col"))
        ]
        df = pd.DataFrame([[NetCompensation.clean_element(td)
                            for td in tr.find_all("td")]
                           for tr in dist_table.find_all("tr")],
                          columns=headers)
        return df.dropna(thresh=2)

    @staticmethod
    def add_subparser(subparsers):
        """
        Args:si
            subparsers: subparsers object to add to
        """
        parser = subparsers.add_parser("netcomp",
                                       help=NetCompensation.__doc__)
        parser.set_defaults(get=NetCompensation.get,
                            output_format="NetCompensation_{year}.{ext}")
        parser.add_argument("--year",
                            default=NetCompensation.default_year,
                            type=int,
                            help="year of data to load")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Loads data tables")

    subparsers = parser.add_subparsers()
    NetCompensation.add_subparser(subparsers)

    args = parser.parse_args()

    table = args.get(**vars(args))

    print(table)
    table.to_csv(args.output_format.format(ext="csv", **vars(args)))
