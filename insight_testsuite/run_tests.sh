#!/bin/bash

declare -r color_start="\033["
declare -r color_red="${color_start}0;31m"
declare -r color_green="${color_start}0;32m"
declare -r color_blue="${color_start}0;34m"
declare -r color_norm="${color_start}0m"

GRADER_ROOT=$(dirname ${BASH_SOURCE})

PROJECT_PATH=${GRADER_ROOT}/..

function print_dir_contents {
  local proj_path=$1
  echo "Project contents:"
  echo -e "${color_blue}$(ls ${proj_path})${color_norm}"
}

function find_file_or_dir_in_project {
  local proj_path=$1
  local file_or_dir_name=$2
  if [[ ! -e "${proj_path}/${file_or_dir_name}" ]]; then
    echo -e "[${color_red}FAIL${color_norm}]: no ${file_or_dir_name} found"
    print_dir_contents ${proj_path}
    echo -e "${color_red}${file_or_dir_name} [MISSING]${color_norm}"
    exit 1
  fi
}

# check project directory structure
function check_project_struct {
  find_file_or_dir_in_project ${PROJECT_PATH} run.sh
  find_file_or_dir_in_project ${PROJECT_PATH} src
  find_file_or_dir_in_project ${PROJECT_PATH} paymo_input
  find_file_or_dir_in_project ${PROJECT_PATH} paymo_output
}

# setup testing output folder
function setup_testing_input_output {
  TEST_OUTPUT_PATH=${GRADER_ROOT}/temp
  if [ -d ${TEST_OUTPUT_PATH} ]; then
    rm -rf ${TEST_OUTPUT_PATH}
  fi

  mkdir -p ${TEST_OUTPUT_PATH}

  cp -r ${PROJECT_PATH}/src ${TEST_OUTPUT_PATH}
  cp -r ${PROJECT_PATH}/run.sh ${TEST_OUTPUT_PATH}
  cp -r ${PROJECT_PATH}/paymo_input ${TEST_OUTPUT_PATH}
  cp -r ${PROJECT_PATH}/paymo_output ${TEST_OUTPUT_PATH}

  rm -r ${TEST_OUTPUT_PATH}/paymo_input/*
  rm -r ${TEST_OUTPUT_PATH}/paymo_output/*
  cp -r ${GRADER_ROOT}/tests/${test_folder}/paymo_input/batch_payment.txt ${TEST_OUTPUT_PATH}/paymo_input/batch_payment.txt
  cp -r ${GRADER_ROOT}/tests/${test_folder}/paymo_input/stream_payment.txt ${TEST_OUTPUT_PATH}/paymo_input/stream_payment.txt
}

function compare_outputs {
  PROJECT_ANSWER_PATH1=${GRADER_ROOT}/temp/paymo_output/output1.txt
  PROJECT_ANSWER_PATH2=${GRADER_ROOT}/temp/paymo_output/output2.txt
  PROJECT_ANSWER_PATH3=${GRADER_ROOT}/temp/paymo_output/output3.txt
  TEST_ANSWER_PATH1=${GRADER_ROOT}/tests/${test_folder}/paymo_output/output1.txt
  TEST_ANSWER_PATH2=${GRADER_ROOT}/tests/${test_folder}/paymo_output/output2.txt
  TEST_ANSWER_PATH3=${GRADER_ROOT}/tests/${test_folder}/paymo_output/output3.txt

  DIFF_RESULT1=$(diff -bB ${PROJECT_ANSWER_PATH1} ${TEST_ANSWER_PATH1} | wc -l)
  if [ "${DIFF_RESULT1}" -eq "0" ] && [ -f ${PROJECT_ANSWER_PATH1} ]; then
    echo -e "[${color_green}PASS${color_norm}]: ${test_folder} (output1.txt)"
    PASS_CNT=$(($PASS_CNT+1))
  else
    echo -e "[${color_red}FAIL${color_norm}]: ${test_folder} (output1.txt)"
    diff ${PROJECT_ANSWER_PATH1} ${TEST_ANSWER_PATH1}
  fi

  DIFF_RESULT2=$(diff -bB ${PROJECT_ANSWER_PATH2} ${TEST_ANSWER_PATH2} | wc -l)
  if [ "${DIFF_RESULT2}" -eq "0" ] && [ -f ${PROJECT_ANSWER_PATH2} ]; then
    echo -e "[${color_green}PASS${color_norm}]: ${test_folder} (output2.txt)"
    PASS_CNT=$(($PASS_CNT+1))
  else
    echo -e "[${color_red}FAIL${color_norm}]: ${test_folder} (output2.txt)"
    diff ${PROJECT_ANSWER_PATH2} ${TEST_ANSWER_PATH2}
  fi

  DIFF_RESULT3=$(diff -bB ${PROJECT_ANSWER_PATH3} ${TEST_ANSWER_PATH3} | wc -l)
  if [ "${DIFF_RESULT3}" -eq "0" ] && [ -f ${PROJECT_ANSWER_PATH3} ]; then
    echo -e "[${color_green}PASS${color_norm}]: ${test_folder} (output3.txt)"
    PASS_CNT=$(($PASS_CNT+1))
  else
    echo -e "[${color_red}FAIL${color_norm}]: ${test_folder} (output3.txt)"
    diff ${PROJECT_ANSWER_PATH3} ${TEST_ANSWER_PATH3}
  fi
}

function run_all_tests {
  TEST_FOLDERS=$(ls ${GRADER_ROOT}/tests)
  NUM_TESTS=$(($(echo $(echo ${TEST_FOLDERS} | wc -w)) * 3))
  PASS_CNT=0

  # Loop through all tests
  for test_folder in ${TEST_FOLDERS}; do

    setup_testing_input_output

    cd ${GRADER_ROOT}/temp
    bash run.sh 2>&1
    cd ../

    compare_outputs
  done

  echo "[$(date)] ${PASS_CNT} of ${NUM_TESTS} tests passed" >> ${GRADER_ROOT}/results.txt
}

check_project_struct
run_all_tests
