import pathlib
import platform
import subprocess
import sys
import zipfile

import innosetup_builder
from attr import Factory, define, field

innosetup_compiler = innosetup_builder.InnosetupCompiler()

OS = platform.system()

@define
class InstallerBuilder:
    app_name = field(converter=str)
    dist_path = field(default='dist', converter=pathlib.Path)
    main_module = field(default='')
    version = field(default='0.0', converter=str)
    author = field(default='', converter=str)
    run_at_startup = field(default=False)
    url = field(default='', converter=str)
    company_name = field(default='')
    include_modules = field(default=Factory(list), converter=list)
    data_files = field(default=Factory(list), converter=list)
    data_directories = field(default=Factory(list), converter=list)
    icon = field(default='')
    icon_index = field(default=0)
    description = field(default='')
    license = field(default='')

    def compile_distribution(self):
        run_nuitka(self.main_module, self.dist_path, app_name=self.app_name, app_version=self.version, company_name=self.company_name, modules_to_include=self.include_modules, include_data_files=self.data_files, include_data_dirs=self.data_directories)

    def create_installer(self):
        innosetup_installer = innosetup_builder.Installer()
        innosetup_installer.app_name = self.app_name
        innosetup_installer.files = innosetup_builder.all_files(self.dist_path / 'main.dist')
        innosetup_installer.app_version = self.version
        innosetup_installer.author = self.author
        innosetup_installer.main_executable = self.dist_path / 'main.build/main.exe'
        innosetup_installer.app_short_description = self.description
        innosetup_installer.run_at_startup = self.run_at_startup
        installer_filename = self.dist_path / (self.app_name + '-' + self.version + '.exe')
        innosetup_compiler.build(innosetup_installer, installer_filename)

    def create_dmg(self):
        dmg_filename = self.dist_path / (self.app_name + '-' + self.version + '.dmg')
        app_path = self.dist_path / 'main.dist'
        subprocess.check_call(['hdiutil', 'create', '-srcfolder', app_path, dmg_filename])

    def create_update(self):
        # makes update zip archive
        update_filename = self.dist_path / (self.app_name + '-' + self.version + '.zip')
        with zipfile.ZipFile(update_filename, 'w') as update_zip:
            files = innosetup_builder.all_files(self.dist_path / 'main.dist')
            for file in files:
                update_zip.write(file)

    def build(self):
        #self.compile_distribution()
        if OS == 'Windows':
            self.create_installer()
        elif OS == 'Darwin':
            self.create_dmg()
        else:
            print('Unsupported OS')
            sys.exit(1)
        self.create_update()
        
def run_nuitka(main_module, output_path='dist', modules_to_include=None, packages_to_include=None, console=False, onefile=False, include_data_files=None, include_data_dirs=None, app_name="", company_name="", app_version=""):
    include_modules = []
    if modules_to_include:
        include_modules = ['--include-module=' +
                           module for module in modules_to_include]
    include_packages = []
    if packages_to_include:
        include_packages = ['--include-package=' +
                            package for package in packages_to_include]
    include_data_files = []
    if include_data_files:
        include_data_files = ['--include-data-files=' +
                              data_file for data_file in include_data_files]
    if include_data_dirs:
        include_data_dirs = ['--include-data-dir=' +
                             data_dir for data_dir in include_data_dirs]
    extra_options = ['--assume-yes-for-downloads', '--output-dir=' + str(output_path)]
    command = [sys  .executable, '-m', 'nuitka', '--standalone', *include_modules,
               *include_packages, *include_data_files, *include_data_dirs, *extra_options, main_module]
    if onefile:
        command.append('--onefile')
    if not console:
        command.append('--windows-disable-console')
        command.append('--macos-disable-console')
        command.append('--macos-create-app-bundle')
    if company_name:
        command.append('--windows-company-name=' + company_name)
    if app_name:
        command.append('--windows-product-name=' + app_name)
        command.append('--macos-app-name=' + app_name)
    if app_version:
        # windows app versions must be in the format 1.0.0.0
        windows_version = app_version.split('.')
        windows_version.extend(['0'] * (4 - len(windows_version)))
        command.append('--windows-product-version=' + '.'.join(windows_version))
        command.append('--macos-app-version=' + app_version)
    subprocess.check_call(command)
