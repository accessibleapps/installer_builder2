import os
import pathlib
import platform
import subprocess
import sys
import zipfile

from attr import Factory, define, field

OS = platform.system()


@define
class InstallerBuilder:
    app_name: str = field(converter=str)
    dist_path: pathlib.Path = field(default='./dist', converter=pathlib.Path)
    main_module: str = field(default='')
    version: str = field(default='0.0', converter=str)
    author: str = field(default='', converter=str)
    run_at_startup: bool = field(default=False)
    console: bool = field(default=False)
    url: str = field(default='', converter=str)
    company_name: str = field(default='')
    include_modules: list = field(default=Factory(list), converter=list)
    include_packages: list = field(default=Factory(list), converter=list)
    ignore_imports: list = field(default=Factory(list), converter=list)
    data_files: list = field(default=Factory(list), converter=list)
    data_directories: list = field(default=Factory(list), converter=list)
    data_file_packages: list = field(default=Factory(list), converter=list)
    icon: str = field(default='')
    description: str = field(default='')
    license: str = field(default='')

    def compile_distribution(self):
        run_nuitka(self.main_module, self.dist_path, app_name=self.app_name, app_version=self.version, company_name=self.company_name,
                   include_modules=self.include_modules, include_data_files=self.data_files, include_data_dirs=self.data_directories, packages_to_include=self.include_packages, data_file_packages=self.data_file_packages, ignore_imports=self.ignore_imports, console=self.console)

    def create_installer(self):
        import innosetup_builder
        innosetup_installer = innosetup_builder.Installer()
        innosetup_installer.app_name = self.app_name
        innosetup_installer.files = innosetup_builder.all_files(
            self.dist_path / 'main.dist')
        innosetup_installer.app_version = self.version
        innosetup_installer.author = self.author
        innosetup_installer.main_executable = self.dist_path / 'main.build/main.exe'
        innosetup_installer.app_short_description = self.description
        innosetup_installer.run_at_startup = self.run_at_startup
        installer_filename = "-".join([self.app_name, self.version, 'setup'])
        innosetup_installer.output_base_filename = installer_filename
        innosetup_compiler = innosetup_builder.InnosetupCompiler()

        innosetup_compiler.build(
            innosetup_installer, self.dist_path)

    def create_dmg(self):
        dmg_filename = self.dist_path / \
            (self.app_name + '-' + self.version + '.dmg')
        dist_path = self.dist_path / 'main.dist'
        # move dist_path/main.app into dist_path/main.dist/
        final_path = dist_path / (self.app_name + '.app')
        original_app = self.dist_path / (self.app_name + '.app')
        original_app.replace(final_path)
        subprocess.check_call(
            ['hdiutil', 'create', '-srcfolder', dist_path, dmg_filename])

    def rename_executable(self):
        # Nuitka always generates an executable as self.dist_path/main.dist/main.exe on windows
        # On Mac, it's self.dist_path/main.app
        # rename it with the applications's name
        if OS == 'Windows':
            main_exe = self.dist_path / 'main.dist' / 'main.exe'
            new_exe = self.dist_path / 'main.dist' / (self.app_name + '.exe')
            main_exe.replace(new_exe)
        elif OS == 'Darwin':
            main_exe = self.dist_path / 'main.app'
            new_exe = self.dist_path / (self.app_name + '.app')
            main_exe.replace(new_exe)

    def create_update_zip(self):
        """ copies all files in self.dist_path/main.dist into a zip file including subfolders
        """
        zip_filename = self.dist_path / \
            (self.app_name + '-' + self.version + '.zip')
        dist_path = self.dist_path / 'main.dist'
        with zipfile.ZipFile(zip_filename, 'w') as zip_file:
            # Using Pathlib, walk the directory tree and compress the files in each folder. the contents of main.dist will be at the root of the zip file
            for file in dist_path.rglob('*'):
                if file.is_file():
                    zip_file.write(file, file.relative_to(
                        dist_path))

    def build(self):
        self.compile_distribution()
        self.rename_executable()
        if OS == 'Windows':
            self.create_installer()
        elif OS == 'Darwin':
            self.create_dmg()
        else:
            print('Unsupported OS')
            sys.exit(1)
        self.create_update_zip()


def run_nuitka(main_module, output_path=pathlib.Path('dist'), include_modules=None, packages_to_include=None, console=False, onefile=False, include_data_files=None, include_data_dirs=None, app_name="", company_name="", app_version="", numpy=False, data_file_packages=None, ignore_imports=None):
    if include_modules is None:
        include_modules = []
    include_modules = ['--include-module=' +
                       module for module in include_modules]
    include_packages = []
    if packages_to_include:
        include_packages = ['--include-package=' +
                            include_ for include_ in packages_to_include]
    if include_data_files is None:
        include_data_files = []
    include_data_files = ['--include-data-files=' +
                          data_file for data_file in _format_nuitka_datafiles(include_data_files)]
    if include_data_dirs is None:
        include_data_dirs = []
    include_data_dirs = ['--include-data-dir=' +
                         data_dir for data_dir in _format_nuitka_datafiles(include_data_dirs)]
    if data_file_packages is None:
        data_file_packages = []
    data_file_packages = ['--include-package-data=' +
                          package for package in data_file_packages]
    if ignore_imports is None:
        ignore_imports = []
    ignore_imports = ['--nofollow-import-to=' +
                      ignore for ignore in ignore_imports]
    extra_options = ['--assume-yes-for-downloads',
                     '--output-dir=' + str(output_path)]
    if onefile:
        extra_options.append('--onefile')
    if not console:
        extra_options.append('--windows-disable-console')
        extra_options.append('--macos-disable-console')
        extra_options.append('--macos-create-app-bundle')
    if company_name:
        extra_options.append('--windows-company-name="' + company_name + '"')
    if app_name:
        extra_options.append('--windows-product-name="' + app_name + '"')
        extra_options.append('--macos-app-name=' + app_name)
    if app_version:
        # windows app versions must be in the format 1.0.0.0
        windows_version = app_version.split('.')
        windows_version.extend(['0'] * (4 - len(windows_version)))
        extra_options.append('--windows-product-version=' +
                             '.'.join(windows_version))
        extra_options.append('--macos-app-version=' + app_version)
    if numpy:
        extra_options.append('--enable-plugin=numpy')
    command = [sys  .executable, '-m', 'nuitka', '--standalone', *include_modules,
               *include_packages, *include_data_files, *include_data_dirs, *data_file_packages, *ignore_imports, *extra_options, main_module]
    subprocess.check_call(command)


def _format_nuitka_datafiles(items):
    # datafiles look like path/to/file=path/to/target and we will only get the part before the =
    # copy the tree to the corresponding path
    for item in items:
        if '=-' in item:
            yield item
        yield item + '=' + item
