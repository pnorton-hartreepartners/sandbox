from exchanges_scrapers.platts.download import get_cnx

ftp_path = r'/PRS/Complete'
local_path = r'c:/Temp'

fcnx = get_cnx()
fcnx.cwd(ftp_path)
folders = sorted(fcnx.listdir())

# theres some history folders so we get the latest
latest_folder = folders[-1]
ftp_path = ftp_path + r'/' + latest_folder
fcnx.cwd(ftp_path)

# get the filenames
files = sorted(fcnx.listdir())

for file in files:
    remote_pathfile = ftp_path + r'/' + file
    local_pathfile = local_path + r'/' + file
    print(remote_pathfile)
    fcnx.get(remote_pathfile, local_pathfile)

