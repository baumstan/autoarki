<?php
$access_key 		= "AKIASQKBQCZ2NOBWFMZQ"; //Access Key
$secret_key 		= "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"; //Secret Key
$my_bucket			= "uploads-archidoc-checker"; //bucket name
$region				= "us-east-2"; //bucket region
$success_redirect	= 'http://'. $_SERVER['SERVER_NAME'] . $_SERVER['REQUEST_URI']; //URL to which the client is redirected upon success (currently self)
$allowd_file_size	= "5000000"; //~5 MB allowed Size

//dates
$short_date 		= gmdate('Ymd'); //short date
$iso_date 			= gmdate("Ymd\THis\Z"); //iso format date
$expiration_date 	= gmdate('Y-m-d\TG:i:s\Z', strtotime('+1 hours')); //policy expiration 1 hour from now

//POST Policy required in order to control what is allowed in the request
//For more info http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-HTTPPOSTConstructPolicy.html
$policy = utf8_encode(json_encode(array(
					'expiration' => $expiration_date,
					'conditions' => array(
						array('acl' => 'public-read'),
						array('bucket' => $my_bucket),
						array('success_action_redirect' => $success_redirect),
						array('starts-with', '$key', ''),
						array('content-length-range', '1', $allowd_file_size),
						array('x-amz-credential' => $access_key.'/'.$short_date.'/'.$region.'/s3/aws4_request'),
						array('x-amz-algorithm' => 'AWS4-HMAC-SHA256'),
						array('X-amz-date' => $iso_date)
						))));

//Signature calculation (AWS Signature Version 4)
//For more info http://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html
$kDate = hash_hmac('sha256', $short_date, 'AWS4' . $secret_key, true);
$kRegion = hash_hmac('sha256', $region, $kDate, true);
$kService = hash_hmac('sha256', "s3", $kRegion, true);
$kSigning = hash_hmac('sha256', "aws4_request", $kService, true);
$signature = hash_hmac('sha256', base64_encode($policy), $kSigning);
?>
