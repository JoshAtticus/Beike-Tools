#!/usr/bin/env python3
"""
ROM Builder GUI - Allwinner V3 Action Camera Tool
Provides a graphical interface for building, flashing, and managing ROMs
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import subprocess
import threading
import os
import sys
import shutil
from datetime import datetime
import re

class ROMBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ROM Builder - Allwinner V3 Action Camera")
        self.root.geometry("1100x800")
        
        # Set working directory to script location
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.script_dir)
        
        # Configure dark theme colors
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#0078d4',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'frame_bg': '#252526',
            'button_bg': '#0e639c',
            'button_hover': '#1177bb'
        }
        
        # Configure styles
        self.setup_styles()
        
        # Variables for build settings - associate with root window
        self.version_var = tk.StringVar(self.root, value="1.0")
        self.build_num_var = tk.StringVar(self.root, value="1")
        self.product_type_var = tk.StringVar(self.root, value="Beike")
        self.manufacturer_var = tk.StringVar(self.root, value="JoshAtticus")
        
        # Logo files
        self.boot_logo_file = None
        self.shutdown_logo_file = None
        
        self.setup_ui()
    
    def setup_styles(self):
        """Setup ttk styles for dark theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe', background=self.colors['bg'], foreground=self.colors['fg'], 
                       borderwidth=2, relief='solid')
        style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['accent'], 
                       font=('Arial', 10, 'bold'))
        
        style.configure('TButton', background=self.colors['button_bg'], foreground=self.colors['fg'],
                       borderwidth=1, relief='flat', padding=6)
        style.map('TButton', background=[('active', self.colors['button_hover'])])
        
        style.configure('Accent.TButton', background=self.colors['accent'], foreground=self.colors['fg'],
                       font=('Arial', 9, 'bold'))
        style.map('Accent.TButton', background=[('active', self.colors['button_hover'])])
        
        style.configure('TEntry', fieldbackground=self.colors['frame_bg'], foreground=self.colors['fg'],
                       borderwidth=1, insertcolor=self.colors['fg'])
        style.configure('TCombobox', fieldbackground=self.colors['frame_bg'], foreground=self.colors['fg'],
                       background=self.colors['button_bg'], borderwidth=1)
        
        style.configure('TNotebook', background=self.colors['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', background=self.colors['frame_bg'], foreground=self.colors['fg'],
                       padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', self.colors['button_bg'])],
                 foreground=[('selected', self.colors['fg'])])
        
    def setup_ui(self):
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title with icon/styling
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        title = ttk.Label(title_frame, text="🎥 ROM Builder Tool", font=('Arial', 18, 'bold'))
        title.pack(side=tk.LEFT)
        
        subtitle = ttk.Label(title_frame, text="Allwinner V3 Action Camera", 
                            font=('Arial', 10), foreground='gray')
        subtitle.pack(side=tk.LEFT, padx=(10, 0))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Build tab
        build_tab = ttk.Frame(notebook)
        notebook.add(build_tab, text="🔧 Build")
        
        # Flash tab
        flash_tab = ttk.Frame(notebook)
        notebook.add(flash_tab, text="⚡ Flash")
        
        # Backup tab
        backup_tab = ttk.Frame(notebook)
        notebook.add(backup_tab, text="💾 Backup")
        
        # Misc tab
        misc_tab = ttk.Frame(notebook)
        notebook.add(misc_tab, text="🛠️ Misc")
        
        # Setup tab contents
        self.setup_build_tab(build_tab)
        self.setup_flash_tab(flash_tab)
        self.setup_backup_tab(backup_tab)
        self.setup_misc_tab(misc_tab)
        
        # Output frame (shared between tabs)
        output_frame = ttk.LabelFrame(main_frame, text="📋 Output Log", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Text output with scrollbar and styling
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=80, height=12,
                                                     bg=self.colors['frame_bg'], fg=self.colors['fg'],
                                                     insertbackground=self.colors['fg'], borderwidth=0,
                                                     font=('Monaco', 9))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar with color
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, 
                                     bg=self.colors['frame_bg'], fg=self.colors['success'],
                                     anchor=tk.W, padx=10, pady=5, font=('Arial', 9))
        self.status_label.pack(fill=tk.X)
    
    def setup_build_tab(self, parent):
        """Setup the Build tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Build Settings
        settings_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Build Settings", padding="15")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        for i in range(4):
            settings_frame.columnconfigure(i, weight=1)
        
        ttk.Label(settings_frame, text="Version:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)
        ttk.Entry(settings_frame, textvariable=self.version_var, width=18).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        
        ttk.Label(settings_frame, text="Build #:", font=('Arial', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=5, pady=8)
        ttk.Entry(settings_frame, textvariable=self.build_num_var, width=18).grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5, pady=8)
        
        ttk.Label(settings_frame, text="Product:", font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        ttk.Entry(settings_frame, textvariable=self.product_type_var, width=18).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        
        ttk.Label(settings_frame, text="Manufacturer:", font=('Arial', 9, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=5, pady=8)
        ttk.Entry(settings_frame, textvariable=self.manufacturer_var, width=18).grid(row=1, column=3, sticky=(tk.W, tk.E), padx=5, pady=8)
        
        # Build Actions
        action_frame = ttk.LabelFrame(scrollable_frame, text="🎬 Build Actions", padding="15")
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(action_frame, text="1️⃣ Customize ROM Settings", command=self.customize_rom_gui, 
                  style='Accent.TButton').pack(fill=tk.X, pady=(0, 10), ipady=8)
        
        ttk.Button(action_frame, text="2️⃣ Build ROM Image", command=self.build_rom_gui,
                  style='Accent.TButton').pack(fill=tk.X, pady=(0, 10), ipady=8)
        
        ttk.Button(action_frame, text="📄 Extract mtdblock2 to Edit", command=self.extract_mtdblock2_gui).pack(fill=tk.X, ipady=5)
    
    def setup_flash_tab(self, parent):
        """Setup the Flash tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Flash ROM section
        flash_frame = ttk.LabelFrame(scrollable_frame, text="⚡ Flash System ROM", padding="15")
        flash_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(flash_frame, text="Flash any system ROM image (system_v*.bin) to mtdblock2",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(flash_frame, text="⚡ Flash ROM to Device", command=self.flash_rom_gui,
                  style='Accent.TButton').pack(fill=tk.X, ipady=8)
        
        # Full Restore section
        restore_frame = ttk.LabelFrame(scrollable_frame, text="🔄 Full Device Restore", padding="15")
        restore_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(restore_frame, text="Flash complete device image (full_restore_v*.bin) from sector 0\n⚠️  WARNING: This will overwrite ALL partitions!",
                 font=('Arial', 9), foreground=self.colors['warning']).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(restore_frame, text="🔄 Flash Full Restore Image", command=self.full_restore_gui).pack(fill=tk.X, ipady=8)
    
    def setup_backup_tab(self, parent):
        """Setup the Backup tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Backup section
        backup_frame = ttk.LabelFrame(scrollable_frame, text="💾 Backup Device", padding="15")
        backup_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(backup_frame, text="Backup all mtdblocks (0-7) from device via ADB",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(backup_frame, text="💾 Backup Device (ADB)", command=self.backup_device,
                  style='Accent.TButton').pack(fill=tk.X, ipady=8)
        
        # Extract section
        extract_frame = ttk.LabelFrame(scrollable_frame, text="📂 Extract Backups", padding="15")
        extract_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(extract_frame, text="Extract boot/shutdown logos from backed up mtdblocks",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(extract_frame, text="📂 Extract mtdblocks (Logos)", command=self.extract_mtdblocks_gui).pack(fill=tk.X, ipady=5)
        
        # Restore Image section
        restore_frame = ttk.LabelFrame(scrollable_frame, text="📦 Create Restore Image", padding="15")
        restore_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(restore_frame, text="Create full restore image from mtdblock files (0-6)",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(restore_frame, text="📦 Make Full Restore Image", command=self.make_restore_gui).pack(fill=tk.X, ipady=5)
    
    def setup_misc_tab(self, parent):
        """Setup the Misc tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Logo section
        logo_frame = ttk.LabelFrame(scrollable_frame, text="🖼️ Boot Logos", padding="15")
        logo_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(logo_frame, text="Upload and flash custom boot/shutdown logos via ADB",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 10))
        
        drop_frame = ttk.Frame(logo_frame)
        drop_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Boot logo
        boot_container = ttk.Frame(drop_frame)
        boot_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(boot_container, text="Boot Logo (220x176):", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.boot_logo_label = tk.Label(boot_container, text="🖼️ Drop or Click to Select", 
                                       bg=self.colors['frame_bg'], fg='gray',
                                       relief=tk.SOLID, borderwidth=2, cursor="hand2",
                                       padx=20, pady=30, font=('Arial', 10))
        self.boot_logo_label.pack(fill=tk.X)
        self.boot_logo_label.bind("<Button-1>", lambda e: self.select_boot_logo())
        try:
            self.boot_logo_label.drop_target_register(DND_FILES)
            self.boot_logo_label.dnd_bind('<<Drop>>', lambda e: self.on_boot_logo_drop(e))
        except:
            pass
        
        # Shutdown logo
        shutdown_container = ttk.Frame(drop_frame)
        shutdown_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(shutdown_container, text="Shutdown Logo:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.shutdown_logo_label = tk.Label(shutdown_container, text="🖼️ Drop or Click to Select",
                                           bg=self.colors['frame_bg'], fg='gray',
                                           relief=tk.SOLID, borderwidth=2, cursor="hand2",
                                           padx=20, pady=30, font=('Arial', 10))
        self.shutdown_logo_label.pack(fill=tk.X)
        self.shutdown_logo_label.bind("<Button-1>", lambda e: self.select_shutdown_logo())
        try:
            self.shutdown_logo_label.drop_target_register(DND_FILES)
            self.shutdown_logo_label.dnd_bind('<<Drop>>', lambda e: self.on_shutdown_logo_drop(e))
        except:
            pass
        
        ttk.Button(logo_frame, text="📤 Flash Logos to Device (ADB)", 
                  command=self.change_logos_gui, style='Accent.TButton').pack(fill=tk.X, ipady=8)
        
        # Dependencies section
        deps_frame = ttk.LabelFrame(scrollable_frame, text="📦 Dependencies", padding="15")
        deps_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(deps_frame, text="Check and install required dependencies",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 10))
        
        # Dependencies list
        dep_list_frame = ttk.Frame(deps_frame)
        dep_list_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dep_status_labels = {}
        dependencies = [
            ("Homebrew", "brew install wget", "Package manager for macOS"),
            ("squashfs-tools", "brew install squashfs", "Required for building/extracting ROM"),
            ("libusb", "brew install libusb", "Required for sunxi-tools"),
            ("pkg-config", "brew install pkg-config", "Required for sunxi-tools"),
            ("sunxi-tools", "Install via button below", "Required for flashing device"),
            ("adb", "brew install android-platform-tools", "Required for ADB operations"),
        ]
        
        for i, (name, install_cmd, desc) in enumerate(dependencies):
            row_frame = ttk.Frame(dep_list_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            self.dep_status_labels[name] = tk.StringVar(value="❓ Unknown")
            ttk.Label(row_frame, textvariable=self.dep_status_labels[name], width=15, 
                     font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(row_frame, text=name, width=18, font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(row_frame, text=desc, font=('Arial', 8), foreground='gray').pack(side=tk.LEFT)
            
            if name != "sunxi-tools":
                ttk.Button(row_frame, text="Install", width=10,
                          command=lambda cmd=install_cmd, n=name: self.install_dependency(cmd, n)).pack(side=tk.RIGHT, padx=5)
        
        # Special button for sunxi-tools
        ttk.Button(deps_frame, text="🔧 Build & Install sunxi-tools", 
                  command=self.install_sunxi_tools).pack(fill=tk.X, ipady=5, pady=(5, 0))
        
        ttk.Button(deps_frame, text="🔄 Refresh Status", 
                  command=self.check_dependencies).pack(fill=tk.X, ipady=5, pady=(5, 0))
        
        # Auto-check dependencies
        self.check_dependencies()
        
    def log(self, message):
        """Add message to output text"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
    def run_command(self, command, shell_script=None):
        parent.rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mousewheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Build Settings frame
        settings_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Build Settings", padding="15")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Grid layout for settings
        for i in range(4):
            settings_frame.columnconfigure(i, weight=1)
        
        ttk.Label(settings_frame, text="Version:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)
        version_entry = ttk.Entry(settings_frame, textvariable=self.version_var, width=18)
        version_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        
        ttk.Label(settings_frame, text="Build #:", font=('Arial', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=5, pady=8)
        build_entry = ttk.Entry(settings_frame, textvariable=self.build_num_var, width=18)
        build_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5, pady=8)
        
        ttk.Label(settings_frame, text="Product:", font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        product_entry = ttk.Entry(settings_frame, textvariable=self.product_type_var, width=18)
        product_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        
        ttk.Label(settings_frame, text="Manufacturer:", font=('Arial', 9, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=5, pady=8)
        mfr_entry = ttk.Entry(settings_frame, textvariable=self.manufacturer_var, width=18)
        mfr_entry.grid(row=1, column=3, sticky=(tk.W, tk.E), padx=5, pady=8)
        
        # Button frame
        button_frame = ttk.LabelFrame(scrollable_frame, text="🎬 Actions", padding="15")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Build section
        build_section = ttk.Frame(button_frame)
        build_section.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(build_section, text="Build & Flash", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        
        btn_frame1 = ttk.Frame(build_section)
        btn_frame1.pack(fill=tk.X)
        
        self.customize_btn = ttk.Button(btn_frame1, text="1️⃣ Customize ROM", command=self.customize_rom_gui, 
                                       style='Accent.TButton', width=25)
        self.customize_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=5)
        
        self.build_btn = ttk.Button(btn_frame1, text="2️⃣ Build ROM", command=self.build_rom_gui,
                                   style='Accent.TButton', width=25)
        self.build_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=5)
        
        self.flash_btn = ttk.Button(btn_frame1, text="3️⃣ Flash ROM", command=self.flash_rom_gui,
                                   style='Accent.TButton', width=25)
        self.flash_btn.pack(side=tk.LEFT, ipady=5)
        
        # Separator
        ttk.Separator(button_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Backup section
        backup_section = ttk.Frame(button_frame)
        backup_section.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(backup_section, text="Backup & Restore", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        
        btn_frame2 = ttk.Frame(backup_section)
        btn_frame2.pack(fill=tk.X)
        
        self.backup_btn = ttk.Button(btn_frame2, text="💾 Backup Device", command=self.backup_device, width=20)
        self.backup_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=3)
        
        self.extract_btn = ttk.Button(btn_frame2, text="📂 Extract mtdblocks", command=self.extract_mtdblocks_gui, width=20)
        self.extract_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=3)
        
        self.make_restore_btn = ttk.Button(btn_frame2, text="📦 Make Restore", command=self.make_restore_gui, width=20)
        self.make_restore_btn.pack(side=tk.LEFT, ipady=3)
        
        btn_frame3 = ttk.Frame(backup_section)
        btn_frame3.pack(fill=tk.X, pady=(10, 0))
        
        self.restore_btn = ttk.Button(btn_frame3, text="⚡ Flash Full Restore", command=self.full_restore_gui, width=20)
        self.restore_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=3)
        
        self.extract_single_btn = ttk.Button(btn_frame3, text="📄 Extract mtdblock2", command=self.extract_mtdblock2_gui, width=20)
        self.extract_single_btn.pack(side=tk.LEFT, ipady=3)
        
        # Separator
        ttk.Separator(button_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Logo section
        logo_section = ttk.Frame(button_frame)
        logo_section.pack(fill=tk.X)
        
        ttk.Label(logo_section, text="Boot Logos", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        
        drop_frame = ttk.Frame(logo_section)
        drop_frame.pack(fill=tk.X)
        
        # Boot logo drop zone
        boot_container = ttk.Frame(drop_frame)
        boot_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(boot_container, text="Boot Logo (220x176):", font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 5))
        self.boot_logo_label = tk.Label(boot_container, text="🖼️ Drop or Click to Select", 
                                       bg=self.colors['frame_bg'], fg='gray',
                                       relief=tk.SOLID, borderwidth=2, cursor="hand2",
                                       padx=20, pady=30, font=('Arial', 10))
        self.boot_logo_label.pack(fill=tk.X)
        try:
            self.boot_logo_label.drop_target_register(DND_FILES)
            self.boot_logo_label.dnd_bind('<<Drop>>', lambda e: self.on_boot_logo_drop(e))
        except:
            pass
        
        # Shutdown logo drop zone  
        shutdown_container = ttk.Frame(drop_frame)
        shutdown_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(shutdown_container, text="Shutdown Logo:", font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 5))
        self.shutdown_logo_label = tk.Label(shutdown_container, text="🖼️ Drop or Click to Select",
                                           bg=self.colors['frame_bg'], fg='gray',
                                           relief=tk.SOLID, borderwidth=2, cursor="hand2",
                                           padx=20, pady=30, font=('Arial', 10))
        self.shutdown_logo_label.pack(fill=tk.X)
        try:
            self.shutdown_logo_label.drop_target_register(DND_FILES)
            self.shutdown_logo_label.dnd_bind('<<Drop>>', lambda e: self.on_shutdown_logo_drop(e))
        except:
            pass
        
        flash_btn_frame = ttk.Frame(logo_section)
        flash_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.logos_btn = ttk.Button(flash_btn_frame, text="📤 Flash Logos to Device (ADB)", 
                                   command=self.change_logos_gui, style='Accent.TButton', width=35)
        self.logos_btn.pack(ipady=5)
    
    def setup_deps_tab(self, parent):
        """Setup the dependencies tab"""
        parent.columnconfigure(0, weight=1)
        
        # Instructions
        info_frame = ttk.LabelFrame(parent, text="About", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        info_text = "This tool requires several dependencies to function properly.\nCheck status and install missing dependencies below."
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
        # Dependencies list
        deps_frame = ttk.LabelFrame(parent, text="Dependencies", padding="10")
        deps_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        deps_frame.columnconfigure(1, weight=1)
        
        # Store status labels
        self.dep_status_labels = {}
        
        dependencies = [
            ("Homebrew", "brew", "Package manager for macOS", None),
            ("squashfs-tools", "mksquashfs", "Build and extract squashfs images", "brew install squashfs"),
            ("libusb", "libusb", "USB library for sunxi-tools", "brew install libusb"),
            ("pkg-config", "pkg-config", "Helper tool for compiling", "brew install pkg-config"),
            ("sunxi-tools", "sunxi-fel", "Flash tools for Allwinner devices", "custom"),
            ("adb", "adb", "Android Debug Bridge", "brew install android-platform-tools"),
        ]
        
        row = 0
        for name, check_cmd, description, install_cmd in dependencies:
            # Name
            ttk.Label(deps_frame, text=name, font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            
            # Description
            ttk.Label(deps_frame, text=description, foreground='gray').grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Status
            status_var = tk.StringVar(value="Checking...")
            status_label = ttk.Label(deps_frame, textvariable=status_var, width=15)
            status_label.grid(row=row, column=2, padx=5, pady=5)
            self.dep_status_labels[name] = status_var
            
            # Install button
            if install_cmd:
                if install_cmd == "custom":
                    btn = ttk.Button(deps_frame, text="Install", 
                                   command=lambda: self.install_sunxi_tools(), width=12)
                else:
                    btn = ttk.Button(deps_frame, text="Install", 
                                   command=lambda cmd=install_cmd, n=name: self.install_dependency(cmd, n), width=12)
                btn.grid(row=row, column=3, padx=5, pady=5)
            
            row += 1
        
        # Refresh button
        ttk.Button(deps_frame, text="🔄 Refresh Status", 
                  command=self.check_dependencies, width=20).grid(row=row, column=0, columnspan=4, pady=10)
        
        # Check dependencies on startup
        self.check_dependencies()
        
    def log(self, message):
        """Add message to output text"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
    def run_command(self, command, shell_script=None):
        """Run a command and show output in real-time"""
        try:
            if shell_script:
                # Run shell script
                process = subprocess.Popen(
                    ['bash', shell_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
            else:
                # Run command directly
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
            
            # Read output line by line
            for line in process.stdout:
                self.log(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log("\n✓ Command completed successfully")
                return True
            else:
                self.log(f"\n✗ Command failed with exit code {process.returncode}")
                return False
                
        except Exception as e:
            self.log(f"\n✗ Error: {str(e)}")
            return False
    
    def run_command_list(self, cmd_list):
        """Run a command from a list and show output"""
        try:
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                self.log(line.rstrip())
            
            process.wait()
            return process.returncode == 0
                
        except Exception as e:
            self.log(f"\n✗ Error: {str(e)}")
            return False
    
    def on_boot_logo_drop(self, event):
        """Handle boot logo file drop"""
        file_path = event.data.strip('{}')
        if file_path.lower().endswith(('.jpg', '.jpeg')):
            self.boot_logo_file = file_path
            self.boot_logo_label.config(text=f"✓ {os.path.basename(file_path)}", fg=self.colors['success'])
            self.log(f"Boot logo loaded: {file_path}")
        else:
            messagebox.showerror("Error", "Please drop a JPEG file")
    
    def on_shutdown_logo_drop(self, event):
        """Handle shutdown logo file drop"""
        file_path = event.data.strip('{}')
        if file_path.lower().endswith(('.jpg', '.jpeg')):
            self.shutdown_logo_file = file_path
            self.shutdown_logo_label.config(text=f"✓ {os.path.basename(file_path)}", fg=self.colors['success'])
            self.log(f"Shutdown logo loaded: {file_path}")
        else:
            messagebox.showerror("Error", "Please drop a JPEG file")
    
    def select_boot_logo(self):
        """Fallback: Select boot logo via file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Boot Logo",
            filetypes=[("JPEG files", "*.jpg *.jpeg"), ("All files", "*.*")]
        )
        if file_path:
            self.boot_logo_file = file_path
            self.boot_logo_label.config(text=f"✓ {os.path.basename(file_path)}", fg=self.colors['success'])
            self.log(f"Boot logo loaded: {file_path}")
    
    def select_shutdown_logo(self):
        """Fallback: Select shutdown logo via file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Shutdown Logo",
            filetypes=[("JPEG files", "*.jpg *.jpeg"), ("All files", "*.*")]
        )
        if file_path:
            self.shutdown_logo_file = file_path
            self.shutdown_logo_label.config(text=f"✓ {os.path.basename(file_path)}", fg=self.colors['success'])
            self.log(f"Shutdown logo loaded: {file_path}")
    
    def customize_rom_gui(self):
        """Open customization dialog"""
        CustomizeDialog(self.root, self)
    
    def build_rom_gui(self):
        """Build ROM with GUI"""
        self.output_text.delete(1.0, tk.END)
        
        # Get variables in main thread before starting background thread
        version = self.version_var.get()
        build_num = self.build_num_var.get()
        product_type = self.product_type_var.get()
        manufacturer = self.manufacturer_var.get()
        
        self.status_var.set("Building ROM...")
        self.log("Starting ROM build...")
        self.log("=" * 60)
        self.log(f"Captured settings: v{version}, build#{build_num}, {product_type}, {manufacturer}")
        
        def task():
            try:
                current_date = datetime.now().strftime("%Y%m%d")
                
                if not all([version, build_num, product_type, manufacturer]):
                    self.log("✗ Please fill in all build settings")
                    self.root.after(0, lambda: self.status_var.set("Build failed - missing settings"))
                    return
                
                out_file = f"system_v{version}.bin"
                
                self.log(f"Version: {version}")
                self.log(f"Build Number: {build_num}")
                self.log(f"Product Type: {product_type}")
                self.log(f"Manufacturer: {manufacturer}")
                self.log(f"Build Date: {current_date}\n")
                
                # Update config files
                self.log("Updating firmware information...")
                for cfg_file in ['squashfs-root/res/cfg/220x176.cfg', 'squashfs-root/res/cfg/320x240.cfg']:
                    if os.path.exists(cfg_file):
                        self.log(f"  Updating {cfg_file}")
                        with open(cfg_file, 'r') as f:
                            content = f.read()
                        
                        content = re.sub(r'^product_type=.*', f'product_type={product_type}', content, flags=re.MULTILINE)
                        content = re.sub(r'^software_version=.*', f'software_version={build_num}', content, flags=re.MULTILINE)
                        content = re.sub(r'^updated=.*', f'updated={current_date}', content, flags=re.MULTILINE)
                        content = re.sub(r'^Manufacturer=.*', f'Manufacturer={manufacturer}', content, flags=re.MULTILINE)
                        content = re.sub(r'^date_number=.*', f'date_number={current_date}', content, flags=re.MULTILINE)
                        
                        with open(cfg_file, 'w') as f:
                            f.write(content)
                
                # Build squashfs
                self.log(f"\nCreating {out_file}...")
                exclude_opts = []
                if os.path.exists('.mksquashfs_exclude'):
                    self.log("Using debloat exclusions")
                    exclude_opts = ['-ef', '.mksquashfs_exclude']
                
                cmd = ['mksquashfs', 'squashfs-root', out_file, '-comp', 'xz', '-no-xattrs'] + exclude_opts
                if self.run_command_list(cmd):
                    self.log(f"\n✓ Build complete: {out_file}")
                    self.log(f"To flash: Click 'Flash ROM' button")
                    self.root.after(0, lambda: self.status_var.set("Build complete"))
                else:
                    self.root.after(0, lambda: self.status_var.set("Build failed"))
                    
            except Exception as e:
                self.log(f"\n✗ Error: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("Build error"))
        
        threading.Thread(target=task, daemon=True).start()
    
    def flash_rom_gui(self):
        """Flash ROM to device with GUI"""
        # Find the latest system image
        images = [f for f in os.listdir('.') if f.startswith('system_v') and f.endswith('.bin')]
        if not images:
            messagebox.showerror("Error", "No system image found. Build ROM first.")
            return
        
        image = sorted(images)[-1]  # Get latest
        
        if not messagebox.askyesno("Flash ROM", 
                                   f"Flash {image} to device?\n\n"
                                   "Make sure device is in FEL recovery mode:\n"
                                   "- Remove battery and SD card\n"
                                   "- Hold VOLUME UP\n"
                                   "- Connect USB while holding VOLUME UP"):
            return
        
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Flashing ROM...")
        self.log(f"Flashing {image}...")
        self.log("=" * 60)
        
        def task():
            try:
                os.chdir('sunxi-tools')
                shutil.copy(f'../{image}', image)
                
                # Verify size
                if os.path.exists('../mtdblock2'):
                    img_size = os.path.getsize(image)
                    mtd_size = os.path.getsize('../mtdblock2')
                    
                    if img_size >= mtd_size:
                        self.log(f"✗ Image too large: {img_size} >= {mtd_size} bytes")
                        self.root.after(0, lambda: self.status_var.set("Flash failed - image too large"))
                        os.chdir('..')
                        return
                    self.log(f"Size check passed: {img_size} < {mtd_size} bytes\n")
                
                # Flash
                self.log("Flashing to device...")
                cmd = ['./sunxi-fel', '-p', 'spiflash-write', '2883584', image]
                if self.run_command_list(cmd):
                    self.log("\nResetting device...")
                    subprocess.run(['./sunxi-fel', 'wdreset'])
                    self.log("\n✓ Flash complete! Device is rebooting.")
                    self.root.after(0, lambda: self.status_var.set("Flash complete"))
                else:
                    self.root.after(0, lambda: self.status_var.set("Flash failed"))
                
                os.chdir('..')
                    
            except Exception as e:
                self.log(f"\n✗ Error: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("Flash error"))
                try:
                    os.chdir(self.script_dir)
                except:
                    pass
        
        threading.Thread(target=task, daemon=True).start()
    
    def backup_device(self):
        """Backup device mtdblocks via ADB"""
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Backing up device...")
        self.log("Starting device backup via ADB...")
        self.log("=" * 60)
        
        def task():
            # Create backup directory
            backup_dir = f"backup_{subprocess.check_output(['date', '+%Y%m%d_%H%M%S']).decode().strip()}"
            os.makedirs(backup_dir, exist_ok=True)
            self.log(f"Created backup directory: {backup_dir}")
            
            # Check ADB connection
            try:
                result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
                if 'device' not in result.stdout:
                    self.log("✗ No device connected via ADB")
                    self.root.after(0, lambda: self.status_var.set("Error: No device connected"))
                    return
            except FileNotFoundError:
                self.log("✗ ADB not found. Please install Android Platform Tools")
                self.root.after(0, lambda: self.status_var.set("Error: ADB not found"))
                return
            
            # Backup each mtdblock
            for i in range(8):
                self.log(f"\nBacking up mtdblock{i}...")
                result = subprocess.run(
                    ['adb', 'pull', f'/dev/block/mtdblock{i}', f'{backup_dir}/mtdblock{i}'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.log(f"✓ mtdblock{i} backed up")
                else:
                    self.log(f"✗ Failed to backup mtdblock{i}: {result.stderr}")
            
            self.log(f"\n✓ Backup complete: {backup_dir}/")
            self.root.after(0, lambda: self.status_var.set("Backup complete"))
            
        threading.Thread(target=task, daemon=True).start()
    
    def extract_mtdblocks_gui(self):
        """Extract and process mtdblocks"""
        # File picker for directory
        backup_dir = filedialog.askdirectory(title="Select backup directory with mtdblocks")
        if not backup_dir:
            return
            
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Extracting mtdblocks...")
        self.log(f"Extracting mtdblocks from: {backup_dir}")
        self.log("=" * 60)
        
        def task():
            extract_dir = f"{backup_dir}_extracted"
            os.makedirs(extract_dir, exist_ok=True)
            
            # mtdblock0 - uboot (just copy)
            self.log("\nmtdblock0 (uboot) - copying...")
            if os.path.exists(f"{backup_dir}/mtdblock0"):
                subprocess.run(['cp', f'{backup_dir}/mtdblock0', f'{extract_dir}/uboot.bin'])
                self.log("✓ Copied as uboot.bin")
            
            # mtdblock1 - boot.img (just copy)
            self.log("\nmtdblock1 (boot.img) - copying...")
            if os.path.exists(f"{backup_dir}/mtdblock1"):
                subprocess.run(['cp', f'{backup_dir}/mtdblock1', f'{extract_dir}/boot.img'])
                self.log("✓ Copied as boot.img")
            
            # mtdblock2 - squashfs system
            self.log("\nmtdblock2 (squashfs system) - extracting...")
            if os.path.exists(f"{backup_dir}/mtdblock2"):
                subprocess.run(['cp', f'{backup_dir}/mtdblock2', f'{extract_dir}/system.squashfs'])
                result = subprocess.run(
                    ['unsquashfs', '-d', f'{extract_dir}/squashfs-root', f'{backup_dir}/mtdblock2'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.log("✓ Extracted to squashfs-root/")
                else:
                    self.log(f"✗ Failed to extract: {result.stderr}")
            
            # mtdblock3 - jffs2 data
            self.log("\nmtdblock3 (jffs2 data) - copying...")
            if os.path.exists(f"{backup_dir}/mtdblock3"):
                subprocess.run(['cp', f'{backup_dir}/mtdblock3', f'{extract_dir}/data.jffs2'])
                self.log("✓ Copied as data.jffs2")
                self.log("  (Use jefferson or jffs2dump to extract if needed)")
            
            # mtdblock4 - boot logo
            self.log("\nmtdblock4 (boot logo) - extracting...")
            if os.path.exists(f"{backup_dir}/mtdblock4"):
                # Find JPEG start marker
                with open(f"{backup_dir}/mtdblock4", 'rb') as f:
                    data = f.read()
                jpeg_start = data.find(b'\xff\xd8\xff')
                if jpeg_start != -1:
                    with open(f"{extract_dir}/boot_logo.jpg", 'wb') as out:
                        out.write(data[jpeg_start:])
                    self.log("✓ Extracted as boot_logo.jpg")
                else:
                    subprocess.run(['cp', f'{backup_dir}/mtdblock4', f'{extract_dir}/boot_logo.raw'])
                    self.log("✓ Copied as boot_logo.raw (no JPEG marker found)")
            
            # mtdblock5 - shutdown logo
            self.log("\nmtdblock5 (shutdown logo) - extracting...")
            if os.path.exists(f"{backup_dir}/mtdblock5"):
                with open(f"{backup_dir}/mtdblock5", 'rb') as f:
                    data = f.read()
                jpeg_start = data.find(b'\xff\xd8\xff')
                if jpeg_start != -1:
                    with open(f"{extract_dir}/shutdown_logo.jpg", 'wb') as out:
                        out.write(data[jpeg_start:])
                    self.log("✓ Extracted as shutdown_logo.jpg")
                else:
                    subprocess.run(['cp', f'{backup_dir}/mtdblock5', f'{extract_dir}/shutdown_logo.raw'])
                    self.log("✓ Copied as shutdown_logo.raw (no JPEG marker found)")
            
            self.log(f"\n✓ Extraction complete: {extract_dir}/")
            self.root.after(0, lambda: self.status_var.set("Extraction complete"))
            
        threading.Thread(target=task, daemon=True).start()
    
    def extract_mtdblock2_gui(self):
        """Extract mtdblock2 only"""
        mtdblock2 = filedialog.askopenfilename(title="Select mtdblock2 file", 
                                               filetypes=[("MTD Block", "mtdblock2"), ("All files", "*")])
        if not mtdblock2:
            return
        
        if os.path.exists('squashfs-root'):
            if not messagebox.askyesno("Warning", "squashfs-root exists. Delete and re-extract?"):
                return
            shutil.rmtree('squashfs-root')
        
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Extracting mtdblock2...")
        self.log("Extracting mtdblock2...")
        self.log("=" * 60)
        
        def task():
            try:
                cmd = ['unsquashfs', mtdblock2]
                if self.run_command_list(cmd):
                    self.log("\n✓ Extracted to squashfs-root/")
                    self.root.after(0, lambda: self.status_var.set("Extraction complete"))
                else:
                    self.root.after(0, lambda: self.status_var.set("Extraction failed"))
            except Exception as e:
                self.log(f"\n✗ Error: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("Extraction error"))
        
        threading.Thread(target=task, daemon=True).start()
    
    def full_restore_gui(self):
        """Flash full restore image"""
        images = [f for f in os.listdir('.') if f.startswith('full_restore_v') and f.endswith('.bin')]
        if not images:
            messagebox.showerror("Error", "No restore image found. Create one first.")
            return
        
        image = sorted(images)[-1]
        
        if not messagebox.askyesno("Full Restore", 
                                   f"⚠️  WARNING: FULL RESTORE ⚠️\n\n"
                                   f"This will flash {image} from sector 0.\n"
                                   "This will COMPLETELY OVERWRITE the device.\n\n"
                                   "Device must be in FEL recovery mode.\n\n"
                                   "Continue?"):
            return
        
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Flashing full restore...")
        self.log(f"Flashing {image}...")
        self.log("=" * 60)
        
        def task():
            try:
                os.chdir('sunxi-tools')
                shutil.copy(f'../{image}', image)
                
                self.log("Flashing from sector 0...")
                cmd = ['./sunxi-fel', '-p', 'spiflash-write', '0', image]
                if self.run_command_list(cmd):
                    self.log("\nResetting device...")
                    subprocess.run(['./sunxi-fel', 'wdreset'])
                    self.log("\n✓ Full restore complete! Device is rebooting.")
                    self.root.after(0, lambda: self.status_var.set("Restore complete"))
                else:
                    self.root.after(0, lambda: self.status_var.set("Restore failed"))
                
                os.chdir('..')
                    
            except Exception as e:
                self.log(f"\n✗ Error: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("Restore error"))
                try:
                    os.chdir(self.script_dir)
                except:
                    pass
        
        threading.Thread(target=task, daemon=True).start()
    
    def make_restore_gui(self):
        """Create full restore image"""
        version = simpledialog.askstring("Version", "Enter version (e.g. 1.0):")
        if not version:
            return
        
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Creating restore image...")
        self.log("Creating full restore image...")
        self.log("=" * 60)
        
        def task():
            try:
                if not os.path.exists('mtdblock0'):
                    self.log("✗ mtdblock0 not found (required)")
                    self.root.after(0, lambda: self.status_var.set("Error: mtdblock0 required"))
                    return
                
                blocks = ['mtdblock0']
                for i in range(1, 7):
                    if os.path.exists(f'mtdblock{i}'):
                        blocks.append(f'mtdblock{i}')
                    else:
                        break
                
                self.log(f"Found {len(blocks)} mtdblock files:")
                total_size = 0
                for block in blocks:
                    size = os.path.getsize(block)
                    total_size += size
                    self.log(f"  {block}: {size} bytes")
                
                self.log(f"\nTotal size: {total_size} bytes")
                
                out_file = f"full_restore_v{version}.bin"
                self.log(f"\nCreating {out_file}...")
                
                with open(out_file, 'wb') as outf:
                    for block in blocks:
                        with open(block, 'rb') as inf:
                            outf.write(inf.read())
                
                self.log(f"\n✓ Created {out_file}")
                self.root.after(0, lambda: self.status_var.set("Restore image created"))
                
            except Exception as e:
                self.log(f"\n✗ Error: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("Creation error"))
        
        threading.Thread(target=task, daemon=True).start()
    
    def change_logos_gui(self):
        """Change boot logos via ADB"""
        if not self.boot_logo_file and not self.shutdown_logo_file:
            messagebox.showerror("Error", "Please drop logo files first")
            return
        
        if not messagebox.askyesno("Flash Logos", 
                                   "Flash logos to device via ADB?\n\n"
                                   "Device must be connected with USB debugging enabled."):
            return
        
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Flashing logos...")
        self.log("Flashing logos via ADB...")
        self.log("=" * 60)
        
        def task():
            try:
                # Check ADB
                result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
                if 'device' not in result.stdout:
                    self.log("✗ No device connected via ADB")
                    self.root.after(0, lambda: self.status_var.set("Error: No device"))
                    return
                
                TARGET_SIZE = 131072
                
                # Process boot logo
                if self.boot_logo_file:
                    self.log("\nProcessing boot logo...")
                    with open(self.boot_logo_file, 'rb') as f:
                        data = f.read()
                    
                    if len(data) > TARGET_SIZE:
                        self.log(f"✗ Boot logo too large: {len(data)} bytes")
                        return
                    
                    # Pad to 128KB
                    data += b'\x00' * (TARGET_SIZE - len(data))
                    
                    with open('boot_logo_new.raw', 'wb') as f:
                        f.write(data)
                    
                    self.log("Flashing boot logo...")
                    subprocess.run(['adb', 'push', 'boot_logo_new.raw', '/data/'])
                    subprocess.run(['adb', 'shell', 'toolbox dd if=/data/boot_logo_new.raw of=/dev/block/mtdblock4 bs=131072 && sync'])
                    self.log("✓ Boot logo flashed")
                    os.remove('boot_logo_new.raw')
                
                # Process shutdown logo
                if self.shutdown_logo_file:
                    self.log("\nProcessing shutdown logo...")
                    with open(self.shutdown_logo_file, 'rb') as f:
                        data = f.read()
                    
                    if len(data) > TARGET_SIZE:
                        self.log(f"✗ Shutdown logo too large: {len(data)} bytes")
                        return
                    
                    data += b'\x00' * (TARGET_SIZE - len(data))
                    
                    with open('shutdown_logo_new.raw', 'wb') as f:
                        f.write(data)
                    
                    self.log("Flashing shutdown logo...")
                    subprocess.run(['adb', 'push', 'shutdown_logo_new.raw', '/data/'])
                    subprocess.run(['adb', 'shell', 'toolbox dd if=/data/shutdown_logo_new.raw of=/dev/block/mtdblock5 bs=131072 && sync'])
                    self.log("✓ Shutdown logo flashed")
                    os.remove('shutdown_logo_new.raw')
                
                self.log("\n✓ Done! Power cycle device to see new logos.")
                self.root.after(0, lambda: self.status_var.set("Logos flashed"))
                
            except Exception as e:
                self.log(f"\n✗ Error: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("Logo flash error"))
        
        threading.Thread(target=task, daemon=True).start()
    
    def check_dependencies(self):
        """Check status of all dependencies"""
        def task():
            checks = [
                ("Homebrew", "which brew"),
                ("squashfs-tools", "which mksquashfs"),
                ("libusb", "brew list libusb"),
                ("pkg-config", "which pkg-config"),
                ("sunxi-tools", "test -f sunxi-tools/sunxi-fel && echo found"),
                ("adb", "which adb"),
            ]
            
            for name, cmd in checks:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, timeout=2)
                    if result.returncode == 0:
                        self.root.after(0, lambda n=name: self.dep_status_labels[n].set("✓ Installed"))
                    else:
                        self.root.after(0, lambda n=name: self.dep_status_labels[n].set("✗ Not Found"))
                except:
                    self.root.after(0, lambda n=name: self.dep_status_labels[n].set("✗ Not Found"))
        
        threading.Thread(target=task, daemon=True).start()
    
    def install_dependency(self, install_cmd, name):
        """Install a dependency using the provided command"""
        self.output_text.delete(1.0, tk.END)
        status_msg = f"Installing {name}..."
        self.status_var.set(status_msg)
        self.log(status_msg)
        self.log("=" * 60)
        self.log(f"Command: {install_cmd}\n")
        
        def task():
            try:
                process = subprocess.Popen(
                    install_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    self.log(line.rstrip())
                
                process.wait()
                
                if process.returncode == 0:
                    self.log(f"\n✓ {name} installed successfully")
                    self.root.after(0, lambda: self.status_var.set(f"{name} installed"))
                    self.root.after(100, self.check_dependencies)
                else:
                    self.log(f"\n✗ Installation failed")
                    self.root.after(0, lambda: self.status_var.set(f"Failed to install {name}"))
                    
            except Exception as e:
                self.log(f"\n✗ Error: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("Installation error"))
        
        threading.Thread(target=task, daemon=True).start()
    
    def install_sunxi_tools(self):
        """Install sunxi-tools from source"""
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Installing sunxi-tools...")
        self.log("Installing sunxi-tools from source...")
        self.log("=" * 60)
        
        def task():
            try:
                # Check if directory exists
                if os.path.exists("sunxi-tools"):
                    self.log("sunxi-tools directory already exists")
                    self.log("Updating repository...")
                    os.chdir("sunxi-tools")
                    subprocess.run(["git", "pull"], check=True)
                else:
                    self.log("Cloning sunxi-tools repository...")
                    result = subprocess.run(
                        ["git", "clone", "https://github.com/linux-sunxi/sunxi-tools"],
                        capture_output=True, text=True
                    )
                    self.log(result.stdout)
                    if result.returncode != 0:
                        self.log(result.stderr)
                        self.root.after(0, lambda: self.status_var.set("Failed to clone repository"))
                        return
                    
                    os.chdir("sunxi-tools")
                
                # Build
                self.log("\nBuilding sunxi-tools...")
                self.log("This may take a few minutes...\n")
                
                process = subprocess.Popen(
                    ["make"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    self.log(line.rstrip())
                
                process.wait()
                
                os.chdir("..")
                
                if process.returncode == 0:
                    self.log("\n✓ sunxi-tools built successfully")
                    self.log("  sunxi-fel is now available in sunxi-tools/")
                    self.root.after(0, lambda: self.status_var.set("sunxi-tools installed"))
                    self.root.after(100, self.check_dependencies)
                else:
                    self.log("\n✗ Build failed")
                    self.root.after(0, lambda: self.status_var.set("Build failed"))
                    
            except Exception as e:
                self.log(f"\n✗ Error: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("Installation error"))
                try:
                    os.chdir(self.script_dir)
                except:
                    pass
        
        threading.Thread(target=task, daemon=True).start()


class CustomizeDialog:
    """Dialog for ROM customization settings"""
    def __init__(self, parent, main_app):
        self.main_app = main_app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Customize ROM")
        self.dialog.geometry("600x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable frame
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # WiFi Settings
        wifi_frame = ttk.LabelFrame(scrollable_frame, text="WiFi Settings", padding="10")
        wifi_frame.pack(fill=tk.X, pady=5)
        
        self.wifi_ssid = tk.StringVar(value="Sports DV")
        self.wifi_pwd = tk.StringVar(value="12345678")
        
        ttk.Label(wifi_frame, text="SSID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(wifi_frame, textvariable=self.wifi_ssid, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(wifi_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(wifi_frame, textvariable=self.wifi_pwd, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Menu Settings
        menu_frame = ttk.LabelFrame(scrollable_frame, text="Menu Settings", padding="10")
        menu_frame.pack(fill=tk.X, pady=5)
        
        self.language = tk.StringVar(value="2")
        self.video_res = tk.StringVar(value="0")
        self.photo_res = tk.StringVar(value="4")
        self.gsensor = tk.StringVar(value="1")
        
        ttk.Label(menu_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        lang_combo = ttk.Combobox(menu_frame, textvariable=self.language, width=27, state="readonly")
        lang_combo['values'] = ("0-简体中文", "1-繁體中文", "2-English", "3-日本語", "4-한국어", 
                               "5-Русский", "6-Deutsch", "7-Français", "8-Italiano", "9-Español")
        lang_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(menu_frame, text="Video Resolution:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        video_combo = ttk.Combobox(menu_frame, textvariable=self.video_res, width=27, state="readonly")
        video_combo['values'] = ("0-4K 30FPS", "1-2.7K 30FPS", "2-1080P 60FPS", "3-1080P 30FPS", 
                                "4-720P 120FPS", "5-720P 60FPS", "6-720P 30FPS")
        video_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(menu_frame, text="Photo Resolution:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        photo_combo = ttk.Combobox(menu_frame, textvariable=self.photo_res, width=27, state="readonly")
        photo_combo['values'] = ("0-2M", "1-5M", "2-8M", "3-12M", "4-16M")
        photo_combo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(menu_frame, text="G-Sensor:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        gsensor_combo = ttk.Combobox(menu_frame, textvariable=self.gsensor, width=27, state="readonly")
        gsensor_combo['values'] = ("0-Off", "1-Low", "2-Medium", "3-High")
        gsensor_combo.grid(row=3, column=1, padx=5, pady=5)
        
        # Feature Switches
        switch_frame = ttk.LabelFrame(scrollable_frame, text="Feature Switches", padding="10")
        switch_frame.pack(fill=tk.X, pady=5)
        
        self.power_on_record = tk.BooleanVar(value=False)
        self.record_sound = tk.BooleanVar(value=True)
        self.time_watermark = tk.BooleanVar(value=True)
        self.wifi_enabled = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(switch_frame, text="Power On Record", variable=self.power_on_record).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Checkbutton(switch_frame, text="Record Sound", variable=self.record_sound).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Checkbutton(switch_frame, text="Time Watermark", variable=self.time_watermark).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Checkbutton(switch_frame, text="WiFi", variable=self.wifi_enabled).grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Debloating
        debloat_frame = ttk.LabelFrame(scrollable_frame, text="Debloating", padding="10")
        debloat_frame.pack(fill=tk.X, pady=5)
        
        self.debloat = tk.BooleanVar(value=False)
        ttk.Checkbutton(debloat_frame, text="Enable debloating (exclude fake features & unused drivers)", 
                       variable=self.debloat).pack(anchor=tk.W)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Button(button_frame, text="Apply", command=self.apply).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def apply(self):
        """Apply customization settings"""
        try:
            cfg_dir = "squashfs-root/res/cfg"
            menu_cfg = f"{cfg_dir}/menu.cfg"
            
            # Update WiFi settings
            for cfg_file in [f'{cfg_dir}/220x176.cfg', f'{cfg_dir}/320x240.cfg']:
                if os.path.exists(cfg_file):
                    with open(cfg_file, 'r') as f:
                        content = f.read()
                    content = re.sub(r'^wifi_ssid=.*', f'wifi_ssid={self.wifi_ssid.get()}', content, flags=re.MULTILINE)
                    content = re.sub(r'^wifi_pwd=.*', f'wifi_pwd={self.wifi_pwd.get()}', content, flags=re.MULTILINE)
                    with open(cfg_file, 'w') as f:
                        f.write(content)
            
            # Update menu.cfg
            if os.path.exists(menu_cfg):
                with open(menu_cfg, 'r') as f:
                    content = f.read()
                
                # Extract just the number from combobox value
                lang = self.language.get().split('-')[0]
                vid_res = self.video_res.get().split('-')[0]
                photo_res = self.photo_res.get().split('-')[0]
                gsensor = self.gsensor.get().split('-')[0]
                
                # Update menu settings
                content = re.sub(r'(\[language\].*?current=)\d+', f'\\g<1>{lang}', content, flags=re.DOTALL)
                content = re.sub(r'(\[video_resolution\].*?current=)\d+', f'\\g<1>{vid_res}', content, flags=re.DOTALL)
                content = re.sub(r'(\[photo_resolution\].*?current=)\d+', f'\\g<1>{photo_res}', content, flags=re.DOTALL)
                content = re.sub(r'(\[gsensor\].*?current=)\d+', f'\\g<1>{gsensor}', content, flags=re.DOTALL)
                
                # Update switches
                content = re.sub(r'^power_on_record=.*', f'power_on_record={int(self.power_on_record.get())}', content, flags=re.MULTILINE)
                content = re.sub(r'^record_sound=.*', f'record_sound={int(self.record_sound.get())}', content, flags=re.MULTILINE)
                content = re.sub(r'^time_water_mark=.*', f'time_water_mark={int(self.time_watermark.get())}', content, flags=re.MULTILINE)
                content = re.sub(r'^wifi=.*', f'wifi={int(self.wifi_enabled.get())}', content, flags=re.MULTILINE)
                
                with open(menu_cfg, 'w') as f:
                    f.write(content)
            
            # Handle debloating
            if self.debloat.get():
                with open('.mksquashfs_exclude', 'w') as f:
                    # Add fake feature drivers
                    for driver in ['mma', 'bma']:
                        for root, dirs, files in os.walk('squashfs-root/vendor/modules'):
                            for file in files:
                                if file.startswith(driver):
                                    rel_path = os.path.join(root, file).replace('squashfs-root/', '')
                                    f.write(rel_path + '\n')
                    
                    # Add from exclude.txt
                    if os.path.exists('exclude.txt'):
                        with open('exclude.txt', 'r') as excl:
                            for line in excl:
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    if line.startswith('squashfs-root/'):
                                        line = line.replace('squashfs-root/', '')
                                    f.write(line + '\n')
                
                # Disable fake features in menu
                if os.path.exists(menu_cfg):
                    with open(menu_cfg, 'r') as f:
                        content = f.read()
                    content = re.sub(r'(\[gsensor\].*?count=)\d+', r'\g<1>0', content, flags=re.DOTALL)
                    content = re.sub(r'(\[park_mode\].*?count=)\d+', r'\g<1>0', content, flags=re.DOTALL)
                    with open(menu_cfg, 'w') as f:
                        f.write(content)
            else:
                if os.path.exists('.mksquashfs_exclude'):
                    os.remove('.mksquashfs_exclude')
            
            messagebox.showinfo("Success", "Customization applied successfully!")
            self.main_app.log("✓ ROM customization applied")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings:\n{str(e)}")


def main():
    try:
        root = TkinterDnD.Tk()
        drag_drop_enabled = True
    except Exception as e:
        print(f"Warning: tkinterdnd2 initialization failed: {e}")
        print("Drag & drop will be disabled. Install with: pip3 install tkinterdnd2")
        root = tk.Tk()
        drag_drop_enabled = False
    
    app = ROMBuilderGUI(root)
    
    # Disable drag and drop if not available
    if not drag_drop_enabled:
        app.boot_logo_label.config(text="Boot Logo: Click button to select (220x176)")
        app.shutdown_logo_label.config(text="Shutdown Logo: Click button to select")
        
        # Add click handlers as fallback
        app.boot_logo_label.bind('<Button-1>', lambda e: app.select_boot_logo())
        app.shutdown_logo_label.bind('<Button-1>', lambda e: app.select_shutdown_logo())
    
    root.mainloop()

if __name__ == "__main__":
    main()
