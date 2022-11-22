"""Base types for the dotstrings library."""

from typing import List

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

    value_type: str
    zero_value: str
    one_value: str
    two_value: str
    few_value: str
    many_value: str
    other_value: str

    def __init__(self, contents: dict = None) -> None:
        if contents is None:
            self.value_type = None
            self.zero_value = None
            self.one_value = None
            self.two_value = None
            self.few_value = None
            self.many_value = None
            self.other_value = None
            return

        # Check NSStringFormatSpecTypeKey, should always be NSStringPluralRuleType
        if VARIABLE_VALUE_SPEC_KEY not in contents:
            raise Exception(f"NSStringFormatSpecTypeKey missing in entry")
        if contents[VARIABLE_VALUE_SPEC_KEY] != VARIABLE_VALUE_SPEC_PLURAL:
            raise Exception(f"Value of NSStringFormatSpecTypeKey is not NSStringPluralRuleType")

        # Check NSStringFormatValueTypeKey exists
        # if VARIABLE_VALUE_TYPE_KEY not in contents:
        #    raise Exception(f"NSStringFormatValueTypeKey missing in entry")

        self.value_type = contents.get(VARIABLE_VALUE_TYPE_KEY)
        self.zero_value = contents.get("zero")
        self.one_value = contents.get("one")
        self.two_value = contents.get("two")
        self.few_value = contents.get("few")
        self.many_value = contents.get("many")
        self.other_value = contents.get("other")

    def __repr__(self) -> str:
        """Returns a raw representation of the object which can be used to reconstruct it later.

        :returns: A raw representation of the object
        """
        return str({
            "value_type": self.value_type,
            "zero_value": self.zero_value,
            "one_value": self.one_value,
            "two_value": self.two_value,
            "few_value": self.few_value,
            "many_value": self.many_value,
            "other_value": self.other_value,
        })

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
    variables: dict[str, Variable]

    def __init__(self, key: str, value: str, variables: dict[str, Variable]) -> None:
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

    def merge(self, another) -> None:
        """Merge value from another entry. Values from another entry is preferred
        """

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
