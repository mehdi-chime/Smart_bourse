import config


def main():
    print("=" * 40)
    print(config.PROJECT_NAME)
    print(f"Version : {config.VERSION}")
    print(f"Author  : {config.AUTHOR}")
    print("=" * 40)

    print("Smart Bourse started successfully.")


if __name__ == "__main__":
    main()
