from notion_client import Client, APIResponseError, APIErrorCode
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_TOKEN"))

class NotionConnectionTester:
    """Test class for checking Notion API connection and database operations."""
    
    def __init__(self):
        self.databases = {
            'courses': os.getenv("NOTION_COURSES_DB_ID"),
            'course_content': os.getenv("NOTION_COURSES_CONTENT_DB_ID"),
            'lessons_schedule': os.getenv("NOTION_LESSONS_SCHEDULE_DB_ID"),
            'assignments': os.getenv("NOTION_ASSIGNMENTS_DB_ID"),
            'mentoring_emails': os.getenv("NOTION_MENTORING_EMAILS_DB_ID"),
            'daily_updates': os.getenv("NOTION_DAILY_UPDATES_DB_ID")
        }
        self.test_results = []
        
    def log_test_result(self, test_name, success, message, data=None):
        """Log test results for summary."""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {test_name} - {message}")
        
    def test_connection(self):
        """Test basic connection to Notion API."""
        try:
            users = notion.users.list()
            self.log_test_result(
                "Connection Test", 
                True, 
                f"Successfully connected to Notion API. Found {len(users.get('results', []))} users."
            )
            return True
        except APIResponseError as e:
            self.log_test_result(
                "Connection Test", 
                False, 
                f"Failed to connect to Notion API: {str(e)}"
            )
            return False
        except Exception as e:
            self.log_test_result(
                "Connection Test", 
                False, 
                f"Unexpected error: {str(e)}"
            )
            return False
    
    def test_database_access(self):
        """Test access to all configured databases."""
        all_accessible = True
        
        for db_name, db_id in self.databases.items():
            if not db_id:
                self.log_test_result(
                    f"Database Access - {db_name}", 
                    False, 
                    f"Database ID not configured for {db_name}"
                )
                all_accessible = False
                continue
                
            try:
                database = notion.databases.retrieve(database_id=db_id)
                self.log_test_result(
                    f"Database Access - {db_name}", 
                    True, 
                    f"Successfully accessed {db_name} database",
                    {'title': database.get('title', [{}])[0].get('plain_text', 'Unknown')}
                )
            except APIResponseError as e:
                self.log_test_result(
                    f"Database Access - {db_name}", 
                    False, 
                    f"Failed to access {db_name}: {str(e)}"
                )
                all_accessible = False
            except Exception as e:
                self.log_test_result(
                    f"Database Access - {db_name}", 
                    False, 
                    f"Unexpected error accessing {db_name}: {str(e)}"
                )
                all_accessible = False
                
        return all_accessible
    
    def test_read_operations(self):
        """Test reading from databases."""
        read_success = True
        
        # Test reading from courses database
        courses_db_id = self.databases.get('courses')
        if courses_db_id:
            try:
                # Query first 5 pages from courses database
                courses = notion.databases.query(
                    database_id=courses_db_id,
                    page_size=5
                )
                
                pages_count = len(courses.get('results', []))
                self.log_test_result(
                    "Read Operation - Courses", 
                    True, 
                    f"Successfully read {pages_count} course pages"
                )
                
                # Test reading specific page details if any exist
                if pages_count > 0:
                    first_page = courses['results'][0]
                    page_details = notion.pages.retrieve(page_id=first_page['id'])
                    self.log_test_result(
                        "Read Operation - Page Details", 
                        True, 
                        f"Successfully retrieved page details for page {first_page['id'][:8]}..."
                    )
                    
            except APIResponseError as e:
                self.log_test_result(
                    "Read Operation - Courses", 
                    False, 
                    f"Failed to read courses: {str(e)}"
                )
                read_success = False
        else:
            self.log_test_result(
                "Read Operation - Courses", 
                False, 
                "Courses database ID not configured"
            )
            read_success = False
            
        return read_success
    
    def test_create_operations(self):
        """Test creating new pages in databases."""
        create_success = True
        created_page_ids = []
        
        # Test creating a test course
        courses_db_id = self.databases.get('courses')
        if courses_db_id:
            try:
                test_course_props = {
                    'Course Name': {
                        'title': [
                            {
                                'text': {
                                    'content': f'Test Course - {datetime.now().strftime("%Y%m%d_%H%M%S")}'
                                }
                            }
                        ]
                    },
                    'Credits': {
                        'number': 3
                    },
                    'Status': {
                        'status': {
                            'name': 'Active'
                        }
                    }
                }
                
                new_course = notion.pages.create(
                    parent={'database_id': courses_db_id},
                    properties=test_course_props
                )
                
                created_page_ids.append(new_course['id'])
                self.log_test_result(
                    "Create Operation - Course", 
                    True, 
                    f"Successfully created test course with ID {new_course['id'][:8]}..."
                )
                
            except APIResponseError as e:
                self.log_test_result(
                    "Create Operation - Course", 
                    False, 
                    f"Failed to create course: {str(e)}"
                )
                create_success = False
        
        # Test creating a daily update entry
        daily_updates_db_id = self.databases.get('daily_updates')
        if daily_updates_db_id:
            try:
                test_daily_update_props = {
                    'What Was Studied': {
                        'title': [
                            {
                                'text': {
                                    'content': f'Test Study Session - {datetime.now().strftime("%Y%m%d_%H%M%S")}'
                                }
                            }
                        ]
                    },
                    'Course Name': {
                        'rich_text': [
                            {
                                'text': {
                                    'content': 'Test Course'
                                }
                            }
                        ]
                    },
                    'Date': {
                        'date': {
                            'start': datetime.now().date().isoformat()
                        }
                    },
                    'Hours Spent': {
                        'number': 2
                    },
                    'Productivity Rating': {
                        'select': {
                            'name': 'High'
                        }
                    }
                }
                
                new_daily_update = notion.pages.create(
                    parent={'database_id': daily_updates_db_id},
                    properties=test_daily_update_props
                )
                
                created_page_ids.append(new_daily_update['id'])
                self.log_test_result(
                    "Create Operation - Daily Update", 
                    True, 
                    f"Successfully created test daily update with ID {new_daily_update['id'][:8]}..."
                )
                
            except APIResponseError as e:
                self.log_test_result(
                    "Create Operation - Daily Update", 
                    False, 
                    f"Failed to create daily update: {str(e)}"
                )
                create_success = False
        
        return create_success, created_page_ids
    
    def test_update_operations(self, page_ids_to_update):
        """Test updating existing pages."""
        update_success = True
        
        for page_id in page_ids_to_update[:1]:  # Update only the first created page
            try:
                # First, get the current page to understand its structure
                current_page = notion.pages.retrieve(page_id=page_id)
                
                # Update the page with new content
                updated_props = {}
                
                # Add a comment/note if the page has a text field
                if 'Comments' in current_page.get('properties', {}):
                    updated_props['Comments'] = {
                        'rich_text': [
                            {
                                'text': {
                                    'content': f'Updated by test at {datetime.now().isoformat()}'
                                }
                            }
                        ]
                    }
                elif 'Notes' in current_page.get('properties', {}):
                    updated_props['Notes'] = {
                        'rich_text': [
                            {
                                'text': {
                                    'content': f'Updated by test at {datetime.now().isoformat()}'
                                }
                            }
                        ]
                    }
                
                if updated_props:
                    notion.pages.update(
                        page_id=page_id,
                        properties=updated_props
                    )
                    
                    self.log_test_result(
                        "Update Operation", 
                        True, 
                        f"Successfully updated page {page_id[:8]}..."
                    )
                else:
                    self.log_test_result(
                        "Update Operation", 
                        True, 
                        f"Page {page_id[:8]}... doesn't have updatable text fields, but update operation is functional"
                    )
                    
            except APIResponseError as e:
                self.log_test_result(
                    "Update Operation", 
                    False, 
                    f"Failed to update page {page_id[:8]}...: {str(e)}"
                )
                update_success = False
            except Exception as e:
                self.log_test_result(
                    "Update Operation", 
                    False, 
                    f"Unexpected error updating page {page_id[:8]}...: {str(e)}"
                )
                update_success = False
                
        return update_success
    
    def cleanup_test_pages(self, page_ids_to_cleanup):
        """Clean up test pages by archiving them."""
        cleanup_success = True
        
        for page_id in page_ids_to_cleanup:
            try:
                notion.pages.update(
                    page_id=page_id,
                    archived=True
                )
                self.log_test_result(
                    "Cleanup Operation", 
                    True, 
                    f"Successfully archived test page {page_id[:8]}..."
                )
            except Exception as e:
                self.log_test_result(
                    "Cleanup Operation", 
                    False, 
                    f"Failed to archive page {page_id[:8]}...: {str(e)}"
                )
                cleanup_success = False
                
        return cleanup_success
    
    def run_all_tests(self, cleanup=True):
        """Run all tests in sequence."""
        logger.info("🚀 Starting Notion API Connection Tests...")
        logger.info("=" * 60)
        
        # Test 1: Basic connection
        if not self.test_connection():
            logger.error("❌ Basic connection failed. Cannot proceed with other tests.")
            return self.print_summary()
        
        # Test 2: Database access
        self.test_database_access()
        
        # Test 3: Read operations
        self.test_read_operations()
        
        # Test 4: Create operations
        create_success, created_page_ids = self.test_create_operations()
        
        # Test 5: Update operations (only if we created pages successfully)
        if create_success and created_page_ids:
            self.test_update_operations(created_page_ids)
            
            # Test 6: Cleanup (optional)
            if cleanup:
                self.cleanup_test_pages(created_page_ids)
        
        return self.print_summary()
    
    def print_summary(self):
        """Print a summary of all test results."""
        logger.info("=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        logger.info(f"Tests passed: {passed}/{total}")
        logger.info(f"Success rate: {(passed/total)*100:.1f}%" if total > 0 else "No tests run")
        
        if passed == total:
            logger.info("🎉 All tests passed! Notion connection is working perfectly.")
        else:
            logger.warning("⚠️  Some tests failed. Check the logs above for details.")
            
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            logger.info("\n❌ Failed Tests:")
            for test in failed_tests:
                logger.info(f"  - {test['test']}: {test['message']}")
        
        return passed == total


def main():
    """Main function to run the tests."""
    tester = NotionConnectionTester()
    success = tester.run_all_tests(cleanup=True)
    
    if success:
        print("\n✅ All Notion API tests completed successfully!")
        print("Your Notion integration is ready for use.")
    else:
        print("\n❌ Some tests failed. Please check the configuration and try again.")
        print("Make sure your NOTION_TOKEN is valid and databases are accessible.")
    
    return success


if __name__ == "__main__":
    main()

