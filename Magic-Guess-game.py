def guess_game():
    # Get the end number from the user
    end_number = int(input("Guess any positive number between 1 and :"))

    # Calculate the number of binary digits needed
    binary_digits = len(bin(end_number)) - 2

    # Initialize guessed number
    guessed_number = 0

    # Iterate through each binary digit
    for i in range(binary_digits):
        # Generate and format the table for the current binary digit
        print(f"\nTable {i + 1} :")
        table_numbers = [number for number in range(1, end_number + 1) if number & (1 << i)]
        formatted_table = ', '.join(map(str, table_numbers))
        print(formatted_table)

        # Ask the user if their number is in the table
        response = input("\nIs your number in this table? (yes/no): ").strip().lower()

        # If yes, add the corresponding binary value to the guessed number
        if response.startswith('y'):
            guessed_number += 1 << i

    # Show the guessed number
    print(f"\nYour guessed number is: {guessed_number}")

# To run the game, uncomment the following line in your local environment.
guess_game()
