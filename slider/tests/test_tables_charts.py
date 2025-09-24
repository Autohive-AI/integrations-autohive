# Test add_table and add_chart actions
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def create_test_presentation():
    """Helper to create a test presentation"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "title": "Tables and Charts Test",
            "custom_filename": "test_tables_charts_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", inputs, context)
        return result["presentation_id"], result["file"]

async def test_add_table():
    """Test adding a table to a slide"""
    print("Testing add_table action...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "rows": 4,
            "cols": 3,
            "position": {
                "left": 1.0,
                "top": 2.5,
                "width": 6.0,
                "height": 2.5
            },
            "data": [
                ["Product", "Q1 Sales", "Q2 Sales"],
                ["Honey", "$50,000", "$65,000"],
                ["Beeswax", "$25,000", "$30,000"],
                ["Pollen", "$15,000", "$18,000"]
            ],
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_table", inputs, context)
        
        print(f"✅ Added table:")
        print(f"   Table ID: {result['table_id']}")
        print(f"   Size: 4 rows x 3 columns")
        print(f"   Populated with sales data")
        print(f"   Saved: {result['saved']}")
        
        return result

async def test_add_empty_table():
    """Test adding an empty table"""
    print("\nTesting empty table addition...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "rows": 3,
            "cols": 2,
            "position": {
                "left": 2.0,
                "top": 3.0,
                "width": 4.0,
                "height": 1.5
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_table", inputs, context)
        
        print(f"✅ Added empty table:")
        print(f"   Table ID: {result['table_id']}")
        print(f"   Size: 3 rows x 2 columns")
        print(f"   No data provided - empty cells")
        
        return result

async def test_add_column_chart():
    """Test adding a column chart"""
    print("\nTesting column chart addition...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "chart_type": "column_clustered",
            "position": {
                "left": 1.5,
                "top": 2.0,
                "width": 7.0,
                "height": 3.0
            },
            "data": {
                "categories": ["Spring", "Summer", "Fall", "Winter"],
                "series": [
                    {
                        "name": "Honey Production (lbs)",
                        "values": [45, 120, 85, 20]
                    },
                    {
                        "name": "Bee Population (thousands)",
                        "values": [30, 80, 60, 15]
                    }
                ]
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_chart", inputs, context)
        
        print(f"✅ Added column chart:")
        print(f"   Chart ID: {result['chart_id']}")
        print(f"   Type: Column clustered")
        print(f"   Categories: 4 seasons")
        print(f"   Series: 2 data series")
        
        return result

async def test_add_pie_chart():
    """Test adding a pie chart"""
    print("\nTesting pie chart addition...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "chart_type": "pie",
            "position": {
                "left": 2.0,
                "top": 1.5,
                "width": 5.0,
                "height": 4.0
            },
            "data": {
                "categories": ["Queen", "Workers", "Drones"],
                "series": [
                    {
                        "name": "Colony Composition",
                        "values": [1, 95, 4]
                    }
                ]
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_chart", inputs, context)
        
        print(f"✅ Added pie chart:")
        print(f"   Chart ID: {result['chart_id']}")
        print(f"   Type: Pie chart")
        print(f"   Shows bee colony composition")
        
        return result

async def test_add_line_chart():
    """Test adding a line chart"""
    print("\nTesting line chart addition...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "chart_type": "line",
            "position": {
                "left": 1.0,
                "top": 2.0,
                "width": 8.0,
                "height": 3.0
            },
            "data": {
                "categories": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "series": [
                    {
                        "name": "Hive Temperature (°F)",
                        "values": [45, 48, 55, 65, 75, 85]
                    }
                ]
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_chart", inputs, context)
        
        print(f"✅ Added line chart:")
        print(f"   Chart ID: {result['chart_id']}")
        print(f"   Type: Line chart")
        print(f"   Shows temperature trend over 6 months")
        
        return result

async def main():
    print("Testing Tables and Charts Actions")
    print("=================================")
    
    try:
        await test_add_table()
        await test_add_empty_table()
        await test_add_column_chart()
        await test_add_pie_chart()
        await test_add_line_chart()
        print("\n✅ All tables and charts tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())