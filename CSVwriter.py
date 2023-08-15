import csv
import aiofiles


class CSVwriter:
    def __init__(self):
        self.csv_path = "Results\\result.csv"
        # Field names for header columns of .csv file
        self.field_names = ["url", "title", "description", "emails", "phones", "postal_codes", "inns", "ogrns"]

    async def init_csv(self):
        """Initializes result.csv file"""
        async with aiofiles.open(self.csv_path, 'w', newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            # Write the header row with field names
            await writer.writerow(self.field_names)

    async def fill_csv(self, url: str, title: str, description: str, emails: str, phones: str, postal_codes: str,
                       inns: str, ogrns: str):
        """Appends data to result.csv file"""
        async with aiofiles.open(self.csv_path, 'a', newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            # Write a row with the provided data
            await writer.writerow((url, title, description, emails, phones, postal_codes, inns, ogrns))
