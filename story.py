#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Framework for a document
"""


class Document(object):
    """a full document - for example, a book"""

    def __init__(self, title, chaptersNamed=False):
        self.title = title
        self.namedChapters = chaptersNamed
        self.numChapters = 0
        self.chapters = {}          # if namedChapters is true, keys will be strings of the form "1", "2", ...
                                    # Otherwise, chapters must be named
        self.speakers = {}

    def __str__(self):
        s = self.title
        s += "\t Words: "
        s += self.count_words()
        return s

    def count_words(self):
        return sum([c.count_words for c in self.chapters.values()])

    def get_text(self):
        text = ''
        for chapter in self.chapters.values():
            text += chapter.get_text()
            text += '\n\n\n'
            text += '--------------------'
            text += '\n\n\n'
        return text

    def add_section(self, sectionName='--'):
        if not self.namedChapters:
            sectionName = 'Chapter {}'.format(self.chapters+1)

        self.chapters[sectionName] = Section(self, sectionName)
        self.numChapters += 1

        return self.chapters[sectionName]

    def define_speaker(name, abbreviation):
        self.speakers[name] = Speaker(self, name, abbreviation)
        return self.speakers[name]



class Section(object):
    """a section of a document - for example, a chapter"""

    def __init__(self, parent, title):
        self.story = parent
        self.title = title
        self.paragraphs = []

    def __str__(self):
        pass

    def count_words(self):
        words = sum([p.count_words() for p in self.paragraphs])

    def get_text(self):
        text = ''
        text += self.title.upper()
        text += '\n\n'
        for p in self.paragraphs:
            text += '\t'
            text += p.get_text()
            text += '\n\n'
        return text

    def add_paragraph(self, isDialogue=False, speaker=None):
        if isDialogue:
            newP = Dialogue(self, speaker)
        else:
            newP = Paragraph(self)
        self.paragraphs.append(newP)

        return newP



class Paragraph(object):
    """a paragraph. Use Dialogue class for dialogue."""

    def __init__(self, parent):
        self.section = parent
        self.text = ""

    def __str__(self):
        pass

    def write(self, text):
        self.text = text

    def count_words(self):
        return len(self.text.split(' '))

    def get_text(self):
        return self.text


class Dialogue(Paragraph):
    """a dialogue-only paragraph"""

    def __init__(self, parent, speaker):
        super().__init__(parent)
        self.speaker = speaker
        self.hasTag = None
        self.dialogue = ''
        self.desc = ''

    def write(self, dialogue, desc='', tag=''):
        self.dialogue = dialogue
        if tag != None:
            self.desc = desc
            self.hasTag = True

    def get_dialogue(self):
        if self.hasTag:
            if self.dialogue[-1] == '.':
                self.dialogue[-1] == ','
        return '"' + self.dialogue + '"'

    def get_text(self):
        if self.hasTag:
            return self.get_dialogue() + self.desc
        elif not self.hasTag:
            return self.get_dialogue()


class Speaker(Document):
    """a speaker within a document"""

    def __init__(self, parent, name, abbr):
        self.document = parent
        self.name = name
        self.abbr = abbr
        self.lines = []

    def __str__(self):
        pass

    def add_line(self, dialogue):
        self.lines.append(dialogue)
