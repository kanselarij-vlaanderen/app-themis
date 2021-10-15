#!/usr/bin/env python3
from rdflib import Graph, Namespace, Literal, URIRef
from prompt_toolkit.validation import Validator, ValidationError
import datetime


class DateValidator(Validator):
    def validate(self, document):
        try:
            datetime.date.fromisoformat(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a valid date. Format is YYYY-MM-DD',
                cursor_position=len(document.text))  # Move cursor to end


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # Move cursor to end
