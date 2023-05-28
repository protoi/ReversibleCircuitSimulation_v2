class Gate:
    target, inverted_target, controls, number_of_lines = None, None, None, None

    def __init__(self, target: int, controls: int, number_of_lines: int):
        self.target = target  # binary number with only one 1-bit
        self.inverted_target = bit_flipper(target, number_of_lines)
        self.controls = controls  # which lines are influence the output
        self.number_of_lines = number_of_lines  # number of input lines total

    def generate_output(self, input_lines: int) -> int:
        """
        :param input_lines: integer whose binary representation denotes the input given to the gate
        :type input_lines: int
        :return: Output of the reversible gates given a certain input.
        :rtype:int
        """

        # inverted_target AND input will set the bit at target location to 0
        masked_input = input_lines
        viable_input = masked_input & self.controls

        if viable_input == self.controls:  # inversion is supposed to happen
            return input_lines ^ self.target
        else:
            return input_lines

    def print_gate_info(self):
        print(display(self.controls, self.number_of_lines))


def bit_flipper(num: int, no_of_bits: int) -> int:
    """
    flips the bits of the input and appends 1s to the front for specific lengths.
    Example: num = 100 and no_of_bits = 5.
    The number is essentially 00100 and the
    flipped version is 11011.
    :param num: the number to be flipped.
    :type num: int
    :param no_of_bits: total number of bits (including leading 0's)
    :type no_of_bits: int
    :return: a flipped version of num
    :rtype: int
    """
    temp = (1 << no_of_bits) - 1
    return temp ^ num


def display(num: int, formatting: int) -> str:
    """
    binary representation of a number in string format
    :param num: a number whose binary form is to be displayed
    :type num: int
    :param formatting: number of bits in the binary representation
    :type formatting: int
    :return: a binary string of length formatting which is the binary representation of num
    :rtype: str
    """
    return f'{num:#0{formatting + 2}b}'[2:]
