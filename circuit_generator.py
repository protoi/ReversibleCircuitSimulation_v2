from gate_generator import Gate
from itertools import product
from math import log


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


def generate_pmgf(current_input: int, controls: int):
    """
        Example:
        control =   1111 1100
        input =     1010 1010
        set answer's corresponding bit to 1 for every location where control was 1 but input was 0
        which means answer = 0101 0100,
        but we want to drop any higher order pmgfs (any answer with more than 1 set bit)

        :param current_input: input to the gate, represented by an integer.
        :type current_input: int
        :param controls: a binary number which denotes the current gate of the circuit.
        :type controls: int
        :return: which pmgf is being identified by the gate
        :rtype:  int
    """

    answer = ~current_input & controls
    if bin(answer).count('1') > 1:  # counting set bit
        return 0
    return answer


def produce_multiples_of_2(n: int) -> list[int]:
    """
    takes a number like 110100 and returns a list containing [100000, 010000, 000100]
    When you perform a logical OR on the list or add these numbers up
    it results in the original value of n
    :param n: an integer
    :type n: int
    :return: a list of numbers(powers of 2) when added up produce n
    :rtype: list[int]
    """
    count = 0
    answer = []
    while n != 0:
        if n & 0b1 == 1:
            answer.append(1 << count)
        n = n >> 1
        count += 1
    return answer


class Circuit:
    number_of_lines, cascade_of_gates, starting_data, outputs, smgf, pmgf, mmgf = None, None, None, None, None, None, None

    def __init__(self, number_of_lines: int):
        self.number_of_lines = number_of_lines

    def set_starting_data(self, starting_data: int):
        self.starting_data = starting_data

    def circuit_maker(self, gate_config: list[dict]):
        self.cascade_of_gates = [Gate(config_data['target'], config_data['controls'], self.number_of_lines) for
                                 config_data in gate_config]

    def circuit_user(self, s=True, p=True, m=True):
        """
        fills the values for smgf and pmgf for a certain gate
        :return: None
        :rtype: None
        """
        '''
            initializing 
                outputs: to be a list of integers pre-initialized to 0
                    and of the same length as number of gates in the circuit.
                smgf: a list of booleans pre-initialized to be False 
                    and have the same length as number of gates in the circuit.
                pmgf: a shallow-copy of outputs
                mmgf: an empty list that will grow to (no_of_gatesC2) where every element is a 
                    pair (starting gate, ending gate) such that this pair represents the range of gates that
                    goes missing.
        '''
        no_of_gates = len(self.cascade_of_gates)
        self.outputs = [0 for _ in range(no_of_gates)]
        if s:
            self.smgf = [False for _ in range(no_of_gates)]
        if p:
            self.pmgf = [0 for _ in range(no_of_gates)]
        # self.pmgf_new = copy.copy(self.outputs)

        # self.mmgf = [(0, 0) for _ in range((no_of_gates * (no_of_gates - 1)) // 2)]
        if m:
            self.mmgf = []

        current_output = self.starting_data

        # UNCOMMENT FOR STEP-WISE CIRCUIT INPUT
        # print(f"INPUT: {current_output}")

        for index, gate in enumerate(self.cascade_of_gates):
            '''
                iterating over gate cascade and using
                the previous output of a gate as the input for the next gate
            '''
            current_input = current_output
            current_output = gate.generate_output(current_output)

            # UNCOMMENT FOR STEP-WISE CIRCUIT OUTPUT
            # print(f"{index+1} OUTPUT: {current_output}")

            self.outputs[index] = current_output
            '''
                if every place where controls had a 1 bit, is also 1 in the input.
                This is a test for smgf
            '''
            if current_input & gate.controls == gate.controls:
                if s:
                    self.smgf[
                        index] = True  # need to append current input to this list instead of setting to true or false
                '''
                                                      7 = 00111
                        {'target': 0b10000, 'controls': 0b00111}, -> 0b10111
                        {'target': 0b01000, 'controls': 0b10111}, -> 0b11111
                '''  # print(f'----> for input {current_input}, gate# {index + 1} smgf is handled')
            # otherwise we check if it is a test for pmgf or not
            else:
                # below line was faulty
                if p:
                    self.pmgf[index] = generate_pmgf(current_input, gate.controls)

        # checking for mmgfs
        if m:
            for starting_gate in range(no_of_gates - 1):  # where the gates go missing from
                for ending_gate in range(starting_gate + 1, no_of_gates):  # upto which gate is everything missing
                    output_after_first_gate_removed = self.outputs[starting_gate - 1]

                    # if 1st[0th index] gate goes missing, the circuits original input is propagated up to ending_gate+1
                    if starting_gate == 0:
                        output_after_first_gate_removed = self.starting_data

                    # check for output of  starting_gate - 1 != output of ending_gate -> fault is detectable
                    if output_after_first_gate_removed != self.outputs[ending_gate]:
                        self.mmgf.append((starting_gate, ending_gate))

    def print_outputs(self):
        print(f'for input data: {display(self.starting_data, self.number_of_lines)}')

        for index, outs in enumerate(self.outputs):
            print(f'gate #{index + 1}: output data: ', end='')
            print(display(outs, self.number_of_lines))

    def print_faults(self):
        print(f'smgf:\n{self.smgf}')
        print(f'pmgf:\n{[display(i, self.number_of_lines) for i in self.pmgf]}')
        print(f'mmgf:\n{self.mmgf}')

    def combinations_upon_pmgf(self, gateInfo: Gate):
        template = (display(gateInfo.controls, self.number_of_lines)).replace('0', '{}')
        multiples = produce_multiples_of_2(gateInfo.controls)
        number_of_controls = bin(gateInfo.controls).count('1')  # count the number of ones in the control
        number_of_not_controls = self.number_of_lines - number_of_controls

        def combination(numberOfNonControls) -> list[tuple[int]]:
            return list(product([1, 0], repeat=numberOfNonControls))

        def combination_(numberOfNonControls) -> list[int]:
            return [1 for _ in range(numberOfNonControls)]

        def format_template(fillers: tuple[int]) -> str:
            return template.format(*fillers)

        answer = []
        answer_multis = []

        for combo in combination(number_of_not_controls):
            formatted_template = f'0b{format_template(combo)}'

            formatted_int = int(formatted_template, 2)

            for multi in multiples:
                answer.append(formatted_int ^ multi)
                answer_multis.append(multi)
        # formatted_template = f'0b{format_template(combination_(number_of_not_controls))}'  # formatted_int = int(formatted_template, 2)
        # return [formatted_int ^ multi for multi in multiples]
        return answer, answer_multis

    def traverse_circuit_in_reverse(self, start: int, current_input: int):

        current_output = current_input

        for gate in self.cascade_of_gates[:start + 1][::-1]:  # iterate from start to beginning in reverse order
            current_input, current_output = current_output, gate.generate_output(current_output)

        return current_output

    def explore_pmgf(self):
        no_of_gates = len(self.cascade_of_gates)

        for index, gate in enumerate(reversed(self.cascade_of_gates)):
            gate_number = no_of_gates - index - 1
            results_that_will_cause_pmgf, multis = self.combinations_upon_pmgf(gate)
            inputs_that_will_cause_pmgf = [self.traverse_circuit_in_reverse(gate_number, x) for x in
                                           results_that_will_cause_pmgf]

            # print(f"For Gate #{gate_number} PMGF caused by:\n{inputs_that_will_cause_pmgf}\n")
            print(f"For Gate #{gate_number}")

            for inp, conf in zip(inputs_that_will_cause_pmgf, multis):
                print(f"input -> {display(inp, 5)} | config -> (G #{gate_number}, C #{int(log(conf, 2))})")
