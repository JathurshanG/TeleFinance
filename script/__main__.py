from daily_recap import DailyRecap

def main():
    recap = DailyRecap()
    recap.get_history()
    recap.get_basic_info()

if __name__ == "__main__":
    main()