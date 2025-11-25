#!/bin/bash


count_lines() {
    local file="$1"
    wc -l < "$file"
}

# count_comments() {
#     local file="$1"
#     local extension="${file##*.}"
#     if [[ "$extension" == "c" || "$extension" == "cpp" || "$extension" == "java" ]]; then
#         grep -c '//' "$file"
#     elif [[ "$extension" == "py" ]]; then
#         grep -c '#' "$file"
#     fi
# }

count_comments() {
    local file="$1"
    local extension="${file##*.}"
    if [[ "$extension" == "c" || "$extension" == "cpp" || "$extension" == "java" ]]; then
        local double_back=$(grep -c '//' "$file")
        # local quoted_double_back=$(grep -c '".*//.*"' "$file")
        # local both=$(grep -c '".*//.*".*//' "$file")

        local quoted_double_back=$(grep -c '^[^/]*".*//.*"' "$file")
        local both=$(grep -c '^[^/]*".*//.*".*//' "$file")


        local comment_count=0
        let "comment_count=double_back-quoted_double_back+both" 
        # used inclusion-exclusion p.
        echo "$comment_count" 
    elif [[ "$extension" == "py" ]]; then
        local double_back=$(grep -c '#' "$file")
        local quoted_double_back=$(grep -c '".*#.*"' "$file")
        local both=$(grep -c '".*#.*".*#' "$file")
        local comment_count=0
        let "comment_count=double_back-quoted_double_back+both" 
        # used inclusion-exclusion p.
        echo "$comment_count" 
    fi

}


count_functions() {
    local file="$1"
    local extension="${file##*.}"
    local count=0

    if [[ "$extension" == "py" ]]; then
        count=$(grep -E -c '^\s*(async\s+)?def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*\)\s*:|^\s*[_a-zA-Z][a-zA-Z0-9_]*\s*=\s*lambda\s*.*:' "$file")
    elif [[ "$extension" == "java" ]]; then
        count=$(grep -E -c '^\s*((public|private|protected)\s+)?((static|final|abstract|synchronized|native|strictfp)\s+)*[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*\)\s*\{' "$file")
    elif [[ "$extension" == "c" || "$extension" == "cpp" ]]; then
        count=$(grep -E -c '^\s*[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*\)\s*\{' "$file")
    fi

    echo "$count"
}


unzipFolder() {
    local zip_file=$1
    local target_dir=${2:-.}

    if [[ ! -f "$zip_file" ]]; then
        echo "File $zip_file does not exist."
        return 1
    fi
    local base_name="${zip_file%????}"
    rm -rf "$base_name"
    mkdir -p "$target_dir"
    unzip -q  "$zip_file" -d "$target_dir" 
}


unzip_all() {
    local dir="$1"
    for i in "$dir"/*.zip; do  
        unzipFolder "$i" "$dir"
    done
}


compile_and_run_match() {
    local filename="$1"
    local test_folder="$2"
    local answer_folder="$3"
    local extension="${filename##*.}"
    local src_dir=$(dirname "$filename")

    local matched=0
    local not_matched=0

    if [[ "$extension" == "c" ]]; then
        gcc -o "$src_dir/main.out" "$filename"
    elif [[ "$extension" == "cpp" ]]; then
        g++ -o "$src_dir/main.out" "$filename"
    elif [[ "$extension" == "java" ]]; then
        javac "$filename"
    fi

    for file in "$test_folder"/*.txt; do
        base=$(basename "$file")
        suffix="${base#test}"     
        output_file="$src_dir/out${suffix}"  
        expected_file="$answer_folder/ans${suffix}"

        if [[ "$extension" == "c" || "$extension" == "cpp" ]]; then
            "$src_dir/main.out" < "$file" > "$output_file"
        elif [[ "$extension" == "java" ]]; then
            java -cp "$src_dir" Main < "$file" > "$output_file"
        elif [[ "$extension" == "py" ]]; then
            python3 "$filename" < "$file" > "$output_file"
        fi
  

        if diff -q "$output_file" "$expected_file" >/dev/null; then
            ((matched++))
        else
            ((not_matched++))
        fi
    done
    echo "$matched $not_matched"
}





visit() {
    local visiting_folder="$1"
    local target_folder="$2"
    local test_folder="$3"
    local answer_folder="$4"
    local additional="$5"
    local student_id="$6"
    local student_name="$7"





    local language
    local extension
    local newFileName

    local print=false
    local execute=true
    local count_line=true
    local count_comment=true
    local count_func=true

    [[ "$additional" == *"-v"* ]] && print=true
    [[ "$additional" == *"-noexecute"* ]] && execute=false
    [[ "$additional" == *"-nolc"* ]] && count_line=false
    [[ "$additional" == *"-nocc"* ]] && count_comment=false
    [[ "$additional" == *"-nofc"* ]] && count_func=false
   

# base case:
    if [[ -f "$visiting_folder" ]]; then
        
        extension="${visiting_folder##*.}"
        if [[ "$extension" == "c" ]]; then
            language="C"
            newFileName="main.c"
        elif [[ "$extension" == "cpp" ]]; then
            language="C++"
            newFileName="main.cpp"
        elif [[ "$extension" == "java" ]]; then
            language="Java"
            newFileName="Main.java"
        elif [[ "$extension" == "py" ]]; then
            language="Python"
            newFileName="main.py"
        else
            return
        fi
        if [[ "$print" == true ]]; then
            echo "Organizing files of $student_id"
            if [[ "$execute" == true ]]; then
                echo "Executing files of $student_id"
            fi
        fi
        
        mkdir -p "$target_folder/$language/$student_id"
        cp "$visiting_folder" "$target_folder/$language/$student_id/$newFileName"
        local line_count=0
        local comment_count=0
        local function_count=0
        local matched=0
        local not_matched=0

        if [[ "$count_line" == true ]]; then
            line_count=$(count_lines "$target_folder/$language/$student_id/$newFileName")
        fi
        if [[ "$count_comment" == true ]]; then
            comment_count=$(count_comments "$target_folder/$language/$student_id/$newFileName")
        fi
        if [[ "$count_func" == true ]]; then
            function_count=$(count_functions "$target_folder/$language/$student_id/$newFileName")
        fi

        if [[ "$execute" == true ]]; then
            output=$(compile_and_run_match "$target_folder/$language/$student_id/$newFileName" "$test_folder" "$answer_folder")
            read matched not_matched <<< "$output"
        fi


    
        csv_row="$student_id,\"$student_name\",$language"

        [[ "$execute" == true ]] && csv_row+=",$matched,$not_matched"
        [[ "$count_line" == true ]] && csv_row+=",$line_count"
        [[ "$count_comment" == true ]] && csv_row+=",$comment_count"
        [[ "$count_func" == true ]] && csv_row+=",$function_count"
        echo "$csv_row" >> "$target_folder/result.csv" 

        return
    fi


    for folder in "$visiting_folder"/*; do
        visit "$folder" "$target_folder" "$test_folder" "$answer_folder" "$additional" "$student_id" "$student_name"
    done
}

 



Organize_Submission_and_execute() {
    local submissions_folder="$1"
    local targets_folder="$2"
    local test_folder="$3"
    local answer_folder="$4"
    local additional="$5"

    for submission in "$submissions_folder"/*; do
        if [[ "$submission" != *.zip ]]; then
            student_id="${submission: -7}"
            base=$(basename "$submission")
            student_name=${base%%_*}
            visit "$submission" "$targets_folder" "$test_folder" "$answer_folder" "$additional" "$student_id" "$student_name"
        fi
        
    done
    [[ "$additional" == *"-v"* ]] && echo "All submissions processed successfully"
}


show_usage() {
    echo "Usage: submission_folder target_folder test_folder answer_folder [-v] [-noexecute] [-nolc] [-nocc] [-nofc]"
    echo "Options:"
    echo "  -v          will print useful information while executing scripts"
    echo "  -noexecute  no output files and executable files will be generated,skip matching"
    echo "  -nolc       Skip line counting"
    echo "  -nocc       Skip comment counting"
    echo "  -nofc       Skip function counting"
}

if [[ $# -lt 4 ]]; then
    show_usage
    exit 1
fi

submission_folder="$1"
target_folder="$2"
test_folder="$3"
answer_folder="$4"
shift 4

print=false
execute=true
count_line=true
count_comment=true
count_func=true
optional=""

# for arg in "$@"; do
#     [[ "$arg" == "-v" ]] && print=true && optional+=" $arg"
#     [[ "$arg" == "-noexecute" ]] && execute=false && optional+=" $arg"
#     [[ "$arg" == "-nolc" ]] && count_line=false && optional+=" $arg"
#     [[ "$arg" == "-nocc" ]] && count_comment=false && optional+=" $arg"
#     [[ "$arg" == "-nofc" ]] && count_func=false && optional+=" $arg"
# done

for arg in "$@"; do
    if [[ "$arg" == "-v" ]]; then
        print=true
        optional+=" $arg"
    elif [[ "$arg" == "-noexecute" ]]; then
        execute=false
        optional+=" $arg"
    elif [[ "$arg" == "-nolc" ]]; then
        count_line=false
        optional+=" $arg"
    elif [[ "$arg" == "-nocc" ]]; then
        count_comment=false
        optional+=" $arg"
    elif [[ "$arg" == "-nofc" ]]; then
        count_func=false
        optional+=" $arg"
    else
        show_usage
        exit 1
    fi
done

mkdir -p "$target_folder"
csv_file="$target_folder/result.csv"
touch "$csv_file"
chmod u+rw "$csv_file"

header="student_id,student_name,language"
[[ "$execute" == true ]] && header+=",matched,not_matched"
[[ "$count_line" == true ]] && header+=",line_count"
[[ "$count_comment" == true ]] && header+=",comment_count"
[[ "$count_func" == true ]] && header+=",function_count"

echo "$header" > "$csv_file"


unzip_all "$submission_folder"
Organize_Submission_and_execute "$submission_folder" "$target_folder" "$test_folder" "$answer_folder" "$optional"



# #include <stdio.h>
# //all inclusive test case
# int main() {
#     // This is a real comment
#  printf("This is a string with // fake comment\n"); // Real comment
# char *str = "A tricky one: \"// not a comment\"\\\a"; 
# // Actual comment here
# return 0;
# }