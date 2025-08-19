from scraper import Scraper


def main():
    """Main function"""
    scraper = Scraper()
    try:
        pets = scraper.run_scraper(max_items=100)

        if pets:
            scraper.save_to_csv()

            print(f"\n✅ Successfully scraped {len(pets)} pets!")
            print(f"📁 Data saved to:")
            print("   - petconnect_pets.csv")

        else:
            print("\n❌ No pet data was collected")

    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"\n💥 An error occurred: {e}")
        if scraper.pets_data:
            print(f"💾 Saving {len(scraper.pets_data)} pets collected so far...")
            scraper.save_to_csv()


if __name__ == "__main__":
    main()
