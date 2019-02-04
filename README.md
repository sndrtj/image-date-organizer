# image-date-organizer 

I really like to organize my pictures and images in one central place by date.

While 'big' image organizers like Shotwell and Digikam can do this, I often
find myself 'fixing' their filesystem hierarchy. I just want something _simple_.
I don't need a GUI. 

Basically, this is the layout I want

```
.
├── 2018
│   ├── 01
│   │   ├── 01
│   │   │   ├── 1.jpg
│   │   │   ├── 2.jpg
│   │   │   └── 4.jpg
│   │   └── 02
│   │       └── 5.jpg
│   ├── 02
│   └── 03
└── 2019

```

I.e., organized by year, then by month, and then by day. 

## What this tool should do

1. Function like an image importer, organizing the imported files by date.
2. Optionally remove the source files when done importing.
3. Imports should preferably be transactional.
4. Read EXIF or XMP metadata to acquire the date of images. 
5. Fall back to mtime when EXIF and XMP metadata is not available.
6. Give sensible logging / progress report. 

## What this tool should *not* be

1. Be a database. Let the filesystem be the implicit database.
2. Have a GUI. Let's be strictly CLI-only. 

## What would be nice to have

1. Reading from an MTP device.  


## License
BSD 3-clause  