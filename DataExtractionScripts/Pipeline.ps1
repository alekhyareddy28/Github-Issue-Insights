#Run from root folder
#Usage: .\Pipeline.ps1 <timestamp> <out_file> <pat_location>
python .\DataExtractionScripts\getData.py $args[0]
python .\DataExtractionScripts\scrapIssueEvents.py $args[0] $args[2]
python .\DataExtractionScripts\combine.py $args[0] $args[1]