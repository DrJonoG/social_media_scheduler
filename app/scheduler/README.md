# Scheduler Module

This module handles the scheduling and automated execution of social media posts across multiple platforms.

## Core Components

### `apscheduler.py`
Integrated scheduler that combines APScheduler with post execution logic:
- Background job scheduling with configurable intervals (default: 60 seconds)
- Database polling for scheduled posts due for publication
- Multi-platform posting coordination (Facebook, Instagram, Pinterest, Tumblr, X)
- Status tracking and error reporting
- Media file handling for posts with images/videos
- Automatic credential loading for each platform

### `post_scheduler.py`
Legacy scheduler implementation (deprecated):
- Original standalone scheduler design
- Now superseded by integrated apscheduler.py implementation

## Features

### Scheduling Capabilities
- **Flexible Timing**: Schedule posts for any future date and time
- **Multi-Platform**: Single posts can target multiple platforms simultaneously
- **Batch Processing**: Efficient handling of multiple scheduled posts
- **Time Zone Support**: Configurable time zones for scheduling

### Execution Management
- **Background Operation**: Runs independently of the web interface
- **Error Recovery**: Automatic retry for temporary failures
- **Status Tracking**: Real-time updates on post execution status
- **Logging**: Comprehensive logs for debugging and monitoring

### Platform Integration
- **Unified Interface**: Single scheduling system for all platforms
- **Platform-Specific Handling**: Respects individual platform requirements
- **Credential Management**: Automatic token refresh and validation
- **Rate Limiting**: Respects platform API limits and quotas

## Configuration

### Environment Variables
```env
SCHEDULER_INTERVAL=60  # Check interval in seconds
SCHEDULER_MAX_RETRIES=3  # Maximum retry attempts
SCHEDULER_RETRY_DELAY=300  # Delay between retries in seconds
```

### Database Requirements
The scheduler requires the following database tables:
- `posts`: Stores scheduled post content and timing
- `platform_accounts`: Contains authentication credentials

## Usage

### Starting the Scheduler
The scheduler runs automatically when the main application starts:
```bash
python main.py  # Starts both UI and scheduler
```

### Manual Testing
The scheduler runs automatically as part of the main application. To test posting functionality:
- Use the Streamlit dashboard to schedule posts
- Check terminal output for scheduler activity logs

### Monitoring
- Check application logs for scheduler activity
- Use the dashboard to view pending and completed posts
- Monitor database for post status updates

## Technical Details

### Job Management
- Uses APScheduler's `BackgroundScheduler` for non-blocking operation
- Single recurring job checks for due posts at configurable intervals (default: 60 seconds)
- Integrates directly with platform modules for posting
- Handles media files by creating temporary file-like objects

### Error Handling
- Comprehensive exception handling for network and API errors
- Detailed error logging with context information
- Graceful degradation when platforms are unavailable
- Status updates in database for monitoring

### Performance
- Efficient database queries to minimise load
- Batch processing of multiple posts when possible
- Connection pooling for database operations
- Minimal memory footprint for background operation

## Future Enhancements

- **Priority Queuing**: Support for high-priority posts
- **Content Expiry**: Automatic removal of old scheduled posts
- **Analytics Integration**: Post performance tracking
- **Advanced Retry Logic**: Smarter retry strategies based on error types