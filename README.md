# ActiveCampaign

This simple solution will connect to the ActiveCampaign API using the URL and TOKEN specified in campaign.yml (or another yaml config file).

The solution requires configurations for list, subscribers, message and campaign included in the yaml file.

The solution will return the newly created Campaign ID if successful.


## Test API Connection:

python active_campaign.py -c campaign.yml -t True

## Run Campaign:

python active_campaign.py -c campaign.yml
