import sys
print(sys.path)

from database import run_migrations


def main():
  try:
    print("Running database setup...")
    run_migrations()
    print("Database setup complete.")
  except Exception as e:
      print(f"Error during database setup: {e}")


if __name__ == "__main__":
  main()
