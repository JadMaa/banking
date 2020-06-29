# Write your code here
import random
import sqlite3


class Bank:

    def __init__(self):
        self.bin = '400000'

    def create_card(self):
        customer_card = Card(self.bin)
        print("\nYour card has been created")
        print("Your card number:")
        print(customer_card.card_number)
        print("Your card PIN:")
        print(customer_card.pin + "\n")
        return customer_card

    def log_in(self, conn, card_num, pin):
        cursor = conn.cursor()
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM card WHERE number={card_num});")
        card_exists = cursor.fetchall()[0][0]

        if card_exists:
            cursor.execute(f"SELECT pin FROM card WHERE number={card_num};")
            fetched_pin = cursor.fetchall()[0][0]
            if pin == fetched_pin:
                print("\nYou have successfully logged in!\n")
                return True
            else:
                print("\nWrong card number or PIN!\n")
                return False
        else:
            print("\nWrong card number or PIN!\n")
            return False

    def check_balance(self, conn, card_num):
        cursor = conn.cursor()
        cursor.execute(f"SELECT balance FROM card WHERE number={card_num};")

        fetched_balance = cursor.fetchall()[0][0]
        print(f"\nBalance: {fetched_balance}\n")

    def add_income(self, conn, card_num):
        print("\nEnter income:")
        income_to_add = int(input())

        cursor = conn.cursor()
        cursor.execute(f"UPDATE card SET balance=balance+{income_to_add} WHERE number={card_num};")
        conn.commit()

        print("Income was added!\n")

    def transfer_money(self, conn, card_num):
        print("\nEnter card number:")
        card_num_dest = input()

        if card_num == card_num_dest:
            print("You can't transfer money to the same account!\n")

        elif not self.check_luhn(card_num_dest):
            print("Probably you made mistake in the card number. Please try again!\n")

        else:
            cursor = conn.cursor()
            cursor.execute(f"SELECT EXISTS(SELECT 1 FROM card WHERE number={card_num_dest});")
            card_exists = cursor.fetchall()[0][0]

            if card_exists:
                print("Enter how much money you want to transfer:")
                money = int(input())

                cursor.execute(f"SELECT balance FROM card WHERE number={card_num};")
                current_balance = cursor.fetchall()[0][0]

                if money > current_balance:
                    print("Not enough money!\n")
                else:
                    cursor.execute(f"UPDATE card SET balance=balance-{money} WHERE number={card_num};")
                    cursor.execute(f"UPDATE card SET balance=balance+{money} WHERE number={card_num_dest};")
                    conn.commit()
                    print("Success!\n")
            else:
                print("Such a card does not exist.\n")

    def delete_account(self, conn, card_num):
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM card WHERE number={card_num};")
        conn.commit()

        print("Your account has been closed!\n")

    def check_luhn(self, card_num):
        # reverse the credit card number
        card_num = card_num[::-1]
        # convert to integer list
        card_num = [int(x) for x in card_num]
        # double every second digit
        doubled_second_digit_list = list()
        digits = list(enumerate(card_num, start=1))
        for index, digit in digits:
            if index % 2 == 0:
                doubled_second_digit_list.append(digit * 2)
            else:
                doubled_second_digit_list.append(digit)

        # add the digits if any number is more than 9
        doubled_second_digit_list = [self.sum_digits(x) for x in doubled_second_digit_list]
        # sum all digits
        sum_of_digits = sum(doubled_second_digit_list)
        # return True or False
        return sum_of_digits % 10 == 0

    def sum_digits(self, digit):
        if digit < 10:
            return digit
        else:
            sum = (digit % 10) + (digit // 10)
            return sum

    @staticmethod
    def log_out():
        print("\nYou have successfully logged out!\n")

    @staticmethod
    def print_account_menu():
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        return input()

    @staticmethod
    def print_bank_menu():
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")
        return input()


class Card:
    checksum = '0'

    def __init__(self, bin):
        self.bin = bin
        self.account_id = ''.join(str(random.randint(0, 9)) for n in range(0, 9))
        self.pin = ''.join(str(random.randint(0, 9)) for n in range(0, 4))
        self.balance = 0
        self.checksum = self.generate_checksum()
        self.card_number = self.bin + self.account_id + self.checksum

    def generate_checksum(self):
        card_without_last_digit = self.bin + self.account_id
        temp = []
        sum = 0
        for i in range(0, len(card_without_last_digit)):
            if i % 2 == 0:
                temp.append(int(card_without_last_digit[i]) * 2)
            else:
                temp.append(int(card_without_last_digit[i]))
        for i, item in enumerate(temp):
            if item > 9:
                temp[i] -= 9
            sum += temp[i]

        return str(10 - int(str(sum)[-1:]))


class Database:

    def create_connection(self, db_name):
        conn = None
        try:
            conn = sqlite3.connect(db_name)
        except sqlite3.Error as e:
            print(e)

        return conn

    def create_table(self, conn, create_table_sql):
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except sqlite3.Error as e:
            print(e)

    def create_card(self, conn, card):

        sql_query = f"""INSERT INTO card (number, pin, balance)
                                    VALUES ({card.card_number}, {card.pin}, {card.balance});"""
        cursor = conn.cursor()
        cursor.execute(sql_query)
        conn.commit()


db = Database()
connection = db.create_connection('card.s3db')

create_card_table_query = '''CREATE TABLE IF NOT EXISTS card (
                                id INTEGER PRIMARY KEY,
                                number TEXT,
                                pin TEXT,
                                balance INTEGER DEFAULT 0);'''
db.create_table(connection, create_card_table_query)

bank = Bank()
choice = ''
bank_action = ''

while choice != '0':
    choice = bank.print_account_menu()
    if choice == '1':
        card = bank.create_card()
        db.create_card(connection, card)
    elif choice == '2':
        print("\nEnter your card number:")
        card_num_in = input()
        print("Enter your PIN:")
        pin_in = input()
        if bank.log_in(connection, card_num_in, pin_in):
            while bank_action != '0':
                bank_action = bank.print_bank_menu()
                if bank_action == '1':
                    bank.check_balance(connection, card_num_in)
                elif bank_action == '2':
                    bank.add_income(connection, card_num_in)
                elif bank_action == '3':
                    bank.transfer_money(connection, card_num_in)
                elif bank_action == '4':
                    bank.delete_account(connection, card_num_in)
                    break
                elif bank_action == '5':
                    bank.log_out()
                    break
                elif bank_action == '0':
                    print("\nBye!")
                    exit()
    elif choice == '0':
        connection.close()
        print("\nBye!")
        break
