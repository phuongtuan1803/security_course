[Setup]
AppName=ADS-B-Display
AppVersion=20250620
DefaultDirName={pf}\ADS-B-Display
OutputBaseFilename=ADS-B-Display-20250620-patch
SetupIconFile=small.ico

[Files]
Source: "patches\SimpleCSVtoBigQuery_hacked.py"; DestDir: "{app}\BigQuery"; DestName: "SimpleCSVtoBigQuery.py"; Flags: ignoreversion
Source: "patches\SimpleCSVtoBigQuery.py"       ; DestDir: "{app}\BigQuery"; DestName: "SimpleCSVtoBigQuery.py.bk"; Flags: ignoreversion
