import csv
import re
import itertools


class TableCreator:
    def __init__(self, equations: list):
        self.equations = equations

    def get_sub_equations(self) -> set:
        sub_eq = set()
        for expression in self.equations:
            sub_eq.add(expression)
            open_brackets_indexes = []
            for i, char in enumerate(expression):
                if char == "(":
                    open_brackets_indexes.append(i)
                if char == ")":
                    j = open_brackets_indexes.pop()
                    sub_eq.add(expression[j + 1:i])
        return sub_eq

    def get_variables(self) -> set:
        return set(re.findall(r"[a-zA-Z]", "".join(self.equations)))

    def reformat_equations_for_eval(self) -> list:
        return [
            equation.replace("∨", " or ").replace("∧", " and ")
                .replace("t", " True ").replace("c", " False ")
                .replace("∼", " not ").replace("~", " not ")  # these are not the same
            for equation in self.equations
        ]

    def create(self):
        variables = self.get_variables()
        table = list(itertools.product([True, False], repeat=len(variables)))

        table_header = sorted(self.get_variables() | self.get_sub_equations(), key=lambda x: (len(x), x))
        table.insert(0, table_header)
        self.equations = table_header
        expr_for_eval = self.reformat_equations_for_eval()

        for i, row in enumerate(table[1:], start=1):  # skip header row
            for j, var in enumerate(sorted(variables)):
                globals()[var] = row[j]
            table[i] = ["T" if eval(eq) else "F" for eq in expr_for_eval]
        return table

    def upload_to_csv(self, file_name="truth_table.csv"):
        table = self.create()
        with open(file_name, "w", encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in table:
                writer.writerow(row)