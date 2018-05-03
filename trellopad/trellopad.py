import argparse
import logging
import sys
import requests
import yaml

import furl

from trello import TrelloClient


class TrelloPad:
    def __init__(self):
        self.setup()

    def setup(self):
        self.parse_arguments(sys.argv[1:])
        self.setup_logging()
        self.etherpad = self.parse_etherpad(self.args.url)
        self.trello_content = self.get_etherpad_content()
        self.client = TrelloClient(api_key=self.args.api_key,
                                   api_secret=self.args.api_secret)
        self.configure_variables()

    def configure_variables(self):
        self.board = self.get_trello_board(self.trello_content.get('board'))
        self.epic_list = self.get_list_from_board(
                self.trello_content.get('epic_list', 'Epics'), create=True)
        self.backlog = self.get_list_from_board(
                self.trello_content.get('tasks_list', 'Backlog'), create=True)
        self.label = self.get_label(create=True)

    def setup_logging(self):
        self.log = logging.getLogger('TrelloPad')
        level = logging.DEBUG if self.args.d else logging.INFO
        logging.basicConfig(level=level,
                            format='%(asctime)s %(levelname)s %(name)s: '
                                   '%(message)s')

    def parse_arguments(self, args):
        parser = argparse.ArgumentParser(description='TrelloPad')
        parser.add_argument('--api', required=True, dest='api_key',
                            help='Api to connect to trello')
        parser.add_argument('--token', required=True, dest='api_secret',
                            help='Secret token to connect to trello')
        parser.add_argument('--url', required=True, dest='url',
                            help='Etherpad url')
        parser.add_argument('-d', action='store_true',
                            help='Enable debug mode')
        self.args = parser.parse_args(args)

    def create_card(self, task):
        _list = self.epic_list if task.get('is_epic') else self.backlog

        card_name = task.get('name')
        card_description = task.get('description', '')
        card = _list.add_card(name=card_name,
                              desc=card_description,
                              labels=[self.label])
        for clist in task.get('checklists', []):
            card.add_checklist(clist.get('name'), clist.get('items', []))
        self.log.debug('Card {} created'.format(card.name))
        return card

    def get_etherpad_content(self):
        print(self.etherpad)
        res = requests.get(self.etherpad)
        if res.status_code == 200:
            trello = yaml.load(res.content)
            if len(trello) > 0:
                return trello[0]
        return None

    def parse_etherpad(self, etherpad):
        if 'export/txt' in etherpad:
            return etherpad
        return furl.furl(etherpad).add(path='/export/txt').url

    def generate_trello_cards(self):
        cards = []
        for task in self.trello_content.get('tasks'):
            card = {
                'name': task.get('name'),
                'description': task.get('description'),
                'checklists': task.get('checklists', []),
                'is_epic': False
            }
            cards.append(self.create_card(card))
        card = {
            'name': self.trello_content.get('epic'),
            'description': self.trello_content.get('description'),
            'is_epic': True
        }

        epic_card = self.create_card(card)
        epic_card.add_checklist('List of cards', [c.short_url for c in cards])

    def get_trello_board(self, board_name):
        for board in self.client.list_boards():
            if board.name == board_name:
                return board
        return None

    def get_label(self, create=False):
        for label in self.board.get_labels():
            if label.name == self.trello_content.get('label'):
                return label
        if create:
            self.log.debug('Label {} not found, creating'.format(
                self.trello_content.get('label')))
            return self.board.add_label(
                    self.trello_content.get('label'), 'red')
        return None

    def get_list_from_board(self, list_name, create=False):
        for tlist in self.board.list_lists():
            if tlist.name == list_name and not tlist.closed:
                return tlist
        if create:
            self.log.debug('Board {} not found, creating'.format(list_name))
            return self.board.add_list(list_name)
        return None


if __name__ == '__main__':
    tp = TrelloPad()
    # 'https://etherpad.openstack.org/p/arxcruz-test')
    tp.generate_trello_cards()
