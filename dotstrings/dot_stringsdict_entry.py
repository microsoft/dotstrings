"""Base types for the dotstrings library."""

from typing import Optional

VARIABLE_VALUE_TYPE_KEY = "NSStringFormatValueTypeKey"
VARIABLE_VALUE_SPEC_KEY = "NSStringFormatSpecTypeKey"
FORMAT_KEY = "NSStringLocalizedFormatKey"

VARIABLE_VALUE_SPEC_PLURAL = "NSStringPluralRuleType"


class Variable:
    """Represents a .stringsdict entry variable.

    :param value_type: Value for NSStringFormatValueTypeKey
    :param zero_value: Value for zero
    :param one_value: Value for one
    :param two_value: Value for two
    :param few_value: Value for few
    :param many_value: Value for many
    :param other_value: Value for other
    """

    value_type: Optional[str]
    zero_value: Optional[str]
    one_value: Optional[str]
    two_value: Optional[str]
    few_value: Optional[str]
    many_value: Optional[str]
    other_value: Optional[str]

    def __init__(self) -> None:
        self.value_type = None
        self.zero_value = None
        self.one_value = None
        self.two_value = None
        self.few_value = None
        self.many_value = None
        self.other_value = None

    @staticmethod
    def parse(contents: dict) -> "Variable":
        """Parsing a stringsdict variable entry

        :param contents: The contents of the entry

        :returns: The parsed stringsdict variable entry
        """
        # Check NSStringFormatSpecTypeKey, should always be NSStringPluralRuleType

        variable = Variable()
        if VARIABLE_VALUE_SPEC_KEY not in contents:
            raise Exception("NSStringFormatSpecTypeKey missing in entry")

        if contents[VARIABLE_VALUE_SPEC_KEY] != VARIABLE_VALUE_SPEC_PLURAL:
            raise Exception("Value of NSStringFormatSpecTypeKey is not NSStringPluralRuleType")

        # When initializing from a dict (parsing), be sure NSStringFormatValueTypeKey exists
        if VARIABLE_VALUE_TYPE_KEY not in contents:
            raise Exception("NSStringFormatValueTypeKey missing in entry")

        variable.value_type = contents[VARIABLE_VALUE_TYPE_KEY]

        variable.zero_value = contents.get("zero")
        variable.one_value = contents.get("one")
        variable.two_value = contents.get("two")
        variable.few_value = contents.get("few")
        variable.many_value = contents.get("many")
        variable.other_value = contents.get("other")

        return variable

    def __repr__(self) -> str:
        """Returns a raw representation of the object which can be used to reconstruct it later.

        :returns: A raw representation of the object
        """
        return str(
            {
                "value_type": self.value_type,
                "zero_value": self.zero_value,
                "one_value": self.one_value,
                "two_value": self.two_value,
                "few_value": self.few_value,
                "many_value": self.many_value,
                "other_value": self.other_value,
            }
        )

    def __str__(self) -> str:
        """Generate and return the string representation of the object.

        :return: A string representation of the object
        """
        return self.__repr__()


class DotStringsDictEntry:
    """Represents a .stringsdict entry.

    :param key: The key for the entry
    :param value: The value for the entry
    """

    key: str
    value: str
    variables: dict

    def __init__(self, key: str, value: str, variables: dict) -> None:
        self.key = key
        self.value = value
        self.variables = variables

    def stringsdict_format(self) -> dict:
        """Return the entry as would be formatted in a .stringsdict file

        :returns: The dict representation of this entry
        """
        result = {}
        result[FORMAT_KEY] = self.value
        for variable_name, variable in self.variables.items():
            variable_dict = {}
            variable_dict[VARIABLE_VALUE_SPEC_KEY] = VARIABLE_VALUE_SPEC_PLURAL
            if variable.value_type is not None:
                variable_dict[VARIABLE_VALUE_TYPE_KEY] = variable.value_type
            if variable.zero_value is not None:
                variable_dict["zero"] = variable.zero_value
            if variable.one_value is not None:
                variable_dict["one"] = variable.one_value
            if variable.two_value is not None:
                variable_dict["two"] = variable.two_value
            if variable.few_value is not None:
                variable_dict["few"] = variable.few_value
            if variable.many_value is not None:
                variable_dict["many"] = variable.many_value
            if variable.other_value is not None:
                variable_dict["other"] = variable.other_value

            result[variable_name] = variable_dict

        return result

    def merge(self, another: "DotStringsDictEntry") -> None:
        """Merge value from another entry. Values from another entry is preferred"""

        # We only need to merge variables as key, value should be the same
        for key, variable in self.variables.items():
            another_variable = another.variables.get(key)
            if another_variable is not None:
                variable.value_type = another_variable.value_type
                variable.zero_value = another_variable.zero_value
                variable.one_value = another_variable.one_value
                variable.two_value = another_variable.two_value
                variable.few_value = another_variable.few_value
                variable.many_value = another_variable.many_value
                variable.other_value = another_variable.other_value

    @staticmethod
    def parse(key: str, contents: dict) -> "DotStringsDictEntry":
        """Parsing a stringsdict entry

        :param key: The key of the entry
        :param contents: The contents of the entry

        :returns: The parsed stringsdict entry
        """
        if FORMAT_KEY not in contents:
            raise Exception("NSStringLocalizedFormatKey missing in entry")

        entry_format = contents[FORMAT_KEY]

        variables = {}
        for variable_name, variable_entry in contents.items():
            if variable_name == FORMAT_KEY:
                # Ignore the format key
                continue
            variables[variable_name] = Variable.parse(variable_entry)

        return DotStringsDictEntry(key, entry_format, variables)

    def __repr__(self) -> str:
        """Returns a raw representation of the object which can be used to reconstruct it later.

        :returns: A raw representation of the object
        """
        return str({"key": self.key, "value": self.value, "variables": self.variables})

    def __str__(self) -> str:
        """Generate and return the string representation of the object.

        :return: A string representation of the object
        """
        return self.__repr__()
