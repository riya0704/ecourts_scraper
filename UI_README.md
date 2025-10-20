# eCourts Real-Time Cause List Downloader UI

A modern, responsive web application for downloading cause lists from Indian eCourts in real-time. This application provides an intuitive interface to fetch court data dynamically and download cause lists in PDF format.

## 🚀 Features

### Real-Time Data Fetching
- **Dynamic State Loading**: Fetches all available states from eCourts
- **District Auto-Population**: Loads districts based on selected state
- **Court Complex Discovery**: Retrieves court complexes for selected district
- **Individual Court Listing**: Shows all courts within a complex

### Download Capabilities
- **Single Court Download**: Download cause list for a specific court and date
- **Bulk Complex Download**: Download cause lists for ALL courts in a complex
- **PDF Format**: All downloads are in PDF format
- **ZIP Packaging**: Bulk downloads are packaged in ZIP files

### User Experience
- **Modern UI**: Clean, responsive design that works on all devices
- **Real-Time Feedback**: Loading indicators and progress bars
- **Error Handling**: Graceful error handling with user-friendly messages
- **Fallback Data**: Backup data sources when primary APIs fail

## 📋 Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- Flask
- requests
- beautifulsoup4
- lxml

## 🏃‍♂️ Quick Start

### Method 1: Using Demo Script (Recommended)
```bash
python run_demo.py
```
This will:
- Start the web server
- Automatically open your browser
- Display the application at http://localhost:5000

### Method 2: Manual Start
```bash
python app.py
```
Then open your browser and go to http://localhost:5000

## 📖 How to Use

### Step 1: Select Court Location
1. **Choose State**: Select from the dropdown (loads automatically)
2. **Choose District**: Select district (loads after state selection)
3. **Choose Court Complex**: Select complex (loads after district selection)
4. **Choose Court** (Optional): Select specific court for single downloads

### Step 2: Select Date
- Choose the date for which you want to download the cause list
- Default is today's date

### Step 3: Download
- **Single Court**: Click "Download Single Court Cause List" (requires court selection)
- **All Courts**: Click "Download All Courts in Complex" (downloads all courts in the complex)

## 🔧 API Endpoints

The application provides REST API endpoints:

### GET /api/states
Returns list of all states
```json
[
  {"value": "MH", "text": "Maharashtra"},
  {"value": "DL", "text": "Delhi"}
]
```

### GET /api/districts/{state_code}
Returns districts for a state
```json
[
  {"value": "MH01", "text": "Mumbai City"},
  {"value": "MH02", "text": "Mumbai Suburban"}
]
```

### GET /api/complexes/{state_code}/{district_code}
Returns court complexes for a district
```json
[
  {"value": "MH01C01", "text": "Mumbai City Civil Court"},
  {"value": "MH01C02", "text": "Mumbai Sessions Court"}
]
```

### GET /api/courts/{state_code}/{district_code}/{complex_code}
Returns individual courts in a complex
```json
[
  {"value": "MH01C01CT01", "text": "Court No. 1"},
  {"value": "MH01C01CT02", "text": "Court No. 2"}
]
```

### POST /api/download_single
Download single court cause list
```json
{
  "state_code": "MH",
  "district_code": "MH01",
  "complex_code": "MH01C01",
  "court_code": "MH01C01CT01",
  "date": "2024-10-20"
}
```

### POST /api/download_complex
Download all courts in complex
```json
{
  "state_code": "MH",
  "district_code": "MH01",
  "complex_code": "MH01C01",
  "date": "2024-10-20"
}
```

## 📁 File Structure

```
├── app.py                 # Main Flask application
├── run_demo.py           # Demo script to start the app
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html       # Main UI template
├── downloads/           # Downloaded files (created automatically)
├── static/             # Static files (created automatically)
└── UI_README.md        # This file
```

## 🛠️ Technical Details

### Fallback Mechanisms
The application includes multiple fallback mechanisms:

1. **Primary**: Direct API calls to eCourts
2. **Secondary**: HTML parsing of eCourts pages
3. **Tertiary**: Hardcoded fallback data for major states/districts

### Error Handling
- Network timeouts are handled gracefully
- Invalid responses trigger fallback mechanisms
- User-friendly error messages are displayed
- Progress indicators show operation status

### Security Features
- Input validation on all parameters
- Safe file handling for downloads
- Proper session management
- CSRF protection ready (can be enabled)

## 🔍 Troubleshooting

### Common Issues

**1. No states loading**
- Check internet connection
- eCourts website might be down
- Fallback data will be used automatically

**2. Districts not loading**
- Try refreshing the page
- Select a different state
- Check browser console for errors

**3. Download fails**
- Verify all fields are selected
- Check if the date is valid
- Some courts might not have cause lists for the selected date

**4. Server won't start**
- Make sure port 5000 is not in use
- Install all requirements: `pip install -r requirements.txt`
- Check Python version (3.6+ required)

### Debug Mode
To run in debug mode with detailed error messages:
```bash
export FLASK_DEBUG=1
python app.py
```

## 🌐 Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📱 Mobile Support

The application is fully responsive and works on:
- iOS Safari
- Android Chrome
- Mobile browsers

## 🔮 Future Enhancements

Planned features:
- [ ] Scheduled downloads
- [ ] Email notifications
- [ ] Advanced filtering options
- [ ] Download history
- [ ] Multi-language support
- [ ] Dark mode theme

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review browser console for errors
3. Ensure all requirements are installed
4. Verify internet connectivity to eCourts

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This application interfaces with the official eCourts website. Please use responsibly and in accordance with the website's terms of service.