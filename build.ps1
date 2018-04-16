$url = "https://aka.ms/chakracore/cc_windows_all_1_8_3"
$output = "$PSScriptRoot\cc_windows_all_1_8_3.zip"

# download
if(![System.IO.File]::Exists($output)){
    Invoke-WebRequest -Uri $url -OutFile $output
}

# extract
$extract_output = "$PSScriptRoot\ChakraCodeFiles"
Expand-Archive $output -DestinationPath $extract_output

# copy dll
$folder_name = ""
if([System.IntPtr]::Size -eq 4){
    $folder_name = "x86_release"
}else{
    $folder_name = "x64_release"
}
Copy-Item "$extract_output\$folder_name\ChakraCore.dll" -Destination "$PSScriptRoot\PyChakra"
