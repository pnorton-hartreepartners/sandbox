import os
import pandas as pd

# this is where i dumped the pdfs from one email
folder = r'C:\Users\PNorton\OneDrive - Hartree Partners\Documents\work items\jira\TTDA-1499 Charting project\chart example pdf\gasoline email'

# this is the source of those files
folder2 = r'\\gateway\hetco\P003\Tasks\Excel Reports\Gasoline New Reports\Report'
file_type = '.xlsb'

pdfs = os.listdir(folder)
parts = [file.split('.') for file in pdfs]
stems = [front for front, back in parts]
files = [stem[:-11] + file_type for stem in stems]
filepaths = [os.path.join(folder2, file) for file in files]
data = zip(pdfs, filepaths)
df = pd.DataFrame(data=data, columns=['pdfs', 'filepaths'])
df.to_clipboard()
pass
