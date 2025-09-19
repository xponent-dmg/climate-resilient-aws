from etl import run_etl


def trigger():
    print("ETL triggered—processing now!")
    run_etl()


if __name__ == "__main__":
    trigger()
