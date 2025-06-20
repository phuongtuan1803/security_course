[Setup]
AppName=ADS-B-Display
AppVersion=20250620
DefaultDirName={pf}\ADS-B-Display
OutputBaseFilename=ADS-B-Display-latest
OutputDir=..\static
SetupIconFile=small.ico

[Files]
Source: "patches\SimpleCSVtoBigQuery_hacked.py"; DestDir: "{app}\BigQuery"; DestName: "SimpleCSVtoBigQuery.py"; Flags: ignoreversion
Source: "patches\SimpleCSVtoBigQuery.py"       ; DestDir: "{app}\BigQuery"; DestName: "SimpleCSVtoBigQuery.py.bk"; Flags: ignoreversion
