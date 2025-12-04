import asyncio
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.services.data_service import DataService
from src.api.schemas import DoorItem

async def verify_doors():
    print("Initializing DataService...")
    service = DataService()
    
    # 1. Clear existing doors (manual cleanup if needed, but we'll rely on add for now or just check empty)
    # Note: We don't have a direct clear method exposed in DataService for *just* testing without API, 
    # but we added clear_doors to DataService in previous steps.
    print("Clearing doors...")
    await service.clear_doors()
    
    doors = service.get_all_doors()
    print(f"Doors after clear: {len(doors)}")
    assert len(doors) == 0, "Doors should be empty after clear"

    # 2. Add doors
    print("Adding doors...")
    new_doors = [
        DoorItem(name="Door1", type="normal", area1="Hall", area2="Room1", location="North"),
        DoorItem(name="Door2", type="secure", area1="Hall", area2="ServerRoom", location="South")
    ]
    await service.add_doors(new_doors)
    
    # 3. Verify addition
    doors = service.get_all_doors()
    print(f"Doors after add: {len(doors)}")
    assert len(doors) == 2, "Should have 2 doors"
    
    door1 = service.get_door_info("Door1")
    print(f"Door1 info: {door1}")
    assert door1['type'] == "normal"
    assert door1['area1'] == "Hall"
    
    print("Verification passed!")

if __name__ == "__main__":
    asyncio.run(verify_doors())
