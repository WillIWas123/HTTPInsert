from string import Formatter, ascii_letters
import random


class PayloadFormatter(Formatter):
    def __init__(self):
        super().__init__()

    def _vformat(self, format_string, args, kwargs, used_args, recursion_depth, auto_arg_index=0):
        if recursion_depth < 0:
            raise ValueError('Max string recursion exceeded')
        str_values={}
        int_values={}
        result = []
        for literal_text, field_name, format_spec, conversion in \
                self.parse(format_string):

            # output the literal text
            if literal_text:
                result.append(literal_text)

            # if there's a field, output it
            if field_name is not None:
                # this is some markup, find the object and do
                #  the formatting

                # handle arg indexing when empty field_names are given.
                if field_name == '':
                    if auto_arg_index is False:
                        raise ValueError('cannot switch from manual field '
                                         'specification to automatic field '
                                         'numbering')
                    field_name = str(auto_arg_index)
                    auto_arg_index += 1
                elif field_name.isdigit():
                    if auto_arg_index:
                        raise ValueError('cannot switch from manual field '
                                         'specification to automatic field '
                                         'numbering')
                    # disable auto arg incrementing, if it gets
                    # used later on, then an exception will be raised
                    auto_arg_index = False

                # given the field_name, find the object it references
                #  and the argument it came from
                obj, arg_used = self.get_field(field_name, args, kwargs)
                used_args.add(arg_used)

                # do any conversion on the resulting object
                obj = self.convert_field(obj, conversion)

                # expand the format spec, if needed
                format_spec, auto_arg_index = self._vformat(
                    format_spec, args, kwargs,
                    used_args, recursion_depth-1,
                    auto_arg_index=auto_arg_index)

                # format the object and append to the result
                result.append(self.format_field(obj, format_spec,str_values=str_values,int_values=int_values))

        return ''.join(result), auto_arg_index

    def format_field(self, value, format_spec,str_values=None,int_values=None):
        if not format_spec:
            return value

        if str_values is None:
            str_values={}

        if int_values is None:
            int_values={}

        if isinstance(value, str):
            number = format_spec[3:]
            if format_spec[:3] == "int":
                if int_values.get(number) is None:
                    while True:
                        random_int = str(random.randint(1000,9999))
                        if random_int not in int_values.values():
                            int_values[number] = random_int
                            break
                value = int_values[number]

            elif format_spec[:3] == "str":
                if str_values.get(number) is None:
                    while True:
                        random_str = "".join(random.choices(ascii_letters, k=random.randint(10, 25)))
                        if random_str not in str_values.values():
                            str_values[number] =random_str
                            break

                value = str_values[number]
        return self.format(value, format_spec)

    def get_value(self, key, args, kwargs):
        if isinstance(key, int):
            return args[key]

        elif key == "random": # Replaces "random" as used for generating random strings and integers with an empty string. Only the format_specs is required for setting the random values.
            return ""

        if key not in kwargs.keys():
            return "{"+key+"}"
        return kwargs[key]


def format_payload(payload):
    pf = PayloadFormatter()
    return pf.format(payload)

