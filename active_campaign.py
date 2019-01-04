import requests
import json
import argparse
import sys
import yaml
import datetime
import time


class ApiConn(object):
    def __init__(self, url, token):
        self.url = '{}/api.php?api_key={}'.format(url, token)

    def test(self):
        url = '{}&api_action=group_view&api_output={}&id=3'.format(self.url, 'json')
        res = requests.post(url)
        return json.loads(res.text)['result_message']


class Campaign(ApiConn):
    def __init__(self, url, token, msg_id, list_id):
        super(Campaign, self).__init__(url, token)
        self.msg_id = msg_id
        self.list_id = list_id

    def _timestamp(self):
        ts = datetime.datetime.now() + datetime.timedelta(hours=1, minutes=30)
        return time.strftime('%Y-%m-%d %H:%M:%S', ts.timetuple())

    def create(self, campaign):
        campaign['m[%s]' % self.msg_id] = 100
        campaign['p[%s]' % self.list_id] = self.list_id
        campaign['sdate'] = self._timestamp()
        create_campaign_url = '{}&api_action=campaign_create&api_output=json'.format(self.url)
        res = requests.post(create_campaign_url, data=campaign)
        campaign_id = json.loads(res.text)['id']
        return campaign_id


class List(ApiConn):

    def __init__(self, url, token):
        super(List, self).__init__(url, token)

    def create(self, campaign_list):
        create_campaign_list_url = '{}&api_action=list_add&api_output=json'.format(self.url)
        res = requests.post(create_campaign_list_url, data=campaign_list)
        list_id = json.loads(res.text)['id']
        return list_id


class Subscribers(ApiConn):

    def __init__(self, url, token, list_id):
        super(Subscribers, self).__init__(url, token)
        self.list_id = list_id

    def add(self, subscriber):
        if isinstance(subscriber, list):
            for s in subscriber:
                self.add(s)
        elif isinstance(subscriber, dict):
            subscriber['p[%s]' % self.list_id] = self.list_id
            add_subscriber_url = '%s&api_action=subscriber_add' % (self.url)
            requests.post(add_subscriber_url, data=subscriber)


class Message(ApiConn):

    def __init__(self, url, token, list_id):
        super(Message, self).__init__(url, token)
        self.list_id = list_id

    def add(self, message):
        add_message_url = '{}&api_action=message_add&api_output=json'.format(self.url)
        message['p[%s]' % self.list_id] = self.list_id
        res = requests.post(add_message_url, data=message)
        msg_id = json.loads(res.text)['id']
        return msg_id


def run_simulation(config):

    URL = config['url']
    TOKEN = config['token']

    l = List(URL, TOKEN)
    list_id = l.create(config['list'])

    s = Subscribers(URL, TOKEN, list_id)
    s.add(config['subscribers'])

    m = Message(URL, TOKEN, list_id)
    msg_id = m.add(config['message'])

    c = Campaign(URL, TOKEN, msg_id, list_id)
    campaign_id = c.create(config['message'])

    print('Done creating campaign ID: %s' % campaign_id)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AC Campaign Simulation')
    parser.add_argument('-t', '--test', help='Test the API connection only', required=False, default=False)
    parser.add_argument('-c', '--config', help='YAML configuration file for campaign', required=True, type=str)
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.load(f)

    if args.test:
        t = ApiConn(config['url'], config['token'])
        print t.test()
        sys.exit()

    run_simulation(config)
