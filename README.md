# trellopad
A simple trello - etherpad connection

# About
My team works with Trello and sprints, every week, we need to create a Epic
card, then create a Backlog, with a label, link each card in the epic card in a
checklist, this is boring, take too much time, so I though that there might be
a way to make it easier (link cards to checklist in trello is terrible) so my
idea is create a etherpad where the team can colaborate, in yaml format
(because yaml!) and then run a script that will translate it to trello,
creating the epic, the backlog, linking everything together, descriptions, etc.

# Install
Just install the requirements

::

    pip install -r requirements.txt

# What you will need
You gonna need a api key and api token that you can
(`generated here <https://trello.com/1/appKey/generate>`).

# How to use

python trellopad.py --api apikey --token token --url etherpad_url

# Etherpad format
Format is very easy:

.. code-block:: yaml

    - epic: 'My epic'
      label: 'Label of my sprint'
      description: 'This epic is gonna be epic!'
      epic_list: 'Epics'
      tasks_list: 'Backlog'
      board: 'Trello board name'
      tasks:
        - name: Task 1
          description: Task 1 description
          checklists:
            - name: Checklist 1
              items:
                - Item 1
                - Item 2
            - name: Checklist 2
              items:
                - Item 1
                - item 2
        - name: Task 2
          description: Task 2 description

This is pretty much what you need, then all you need to do is run the script,
and see the magic happens
