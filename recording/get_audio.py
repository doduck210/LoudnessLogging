import sys
import os
import Decklink
import numpy as np


decklink = Decklink.Decklink(0)
decklink.play()
