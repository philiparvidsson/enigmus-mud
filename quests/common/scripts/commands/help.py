# coding=utf-8

""" Provides the help command handler. """

#-----------------------------------------------------------
# IMPORTS
#-----------------------------------------------------------

import messages

from entities import Entity, Player

#-----------------------------------------------------------
# CLASSES
#-----------------------------------------------------------

class Command(Entity):
    """ Command entity for handling the help command. """

    def __init__(self):
        """ Initializes the command. """

        super(Command, self).__init__()

        self.on_message('player_command', self.__player_command,
            filter=messages.for_entities_of_class(Player))

    # ------- MESSAGES -------

    def __player_command(self, player, command):
        if command != 'hjälp':
            return

        player.text('''
Skriv säg &lt;text&gt; för att säga något till andra spelare:
  säg hej, hur går det?

Skriv titta för att se dig omkring. Du kan även titta på eller i något:
  titta
  titta på tavla
  titta i låda

Du kan även plocka upp saker från marken eller behållare:
  ta penna
  ta penna från låda

...och såklart lägga tillbaka saker:
  släng penna
  lägg penna i låda

För att navigera skriver du helt enkelt namnet på den utgång du vill lämna rummet genom. Exempelvis skriver du norr för att gå norrut, och kommer då till nästa rum. Var noga med att läsa av din omgivning. Det finns ledtrådar överallt! Lycka till!
''')
