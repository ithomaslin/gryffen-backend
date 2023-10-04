# Copyright (c) 2023, TradingLab
# All rights reserved.
#
# This file is part of TradingLab.app
# See https://tradinglab.app for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import os
import json
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import Request
from fastapi import HTTPException
from fastapi import status
from gryffen.settings import Settings


load_dotenv()


def private_method(func):

    async def wrapper(request: Request, *args, **kwargs):
        client_ip = request.client.host
        if client_ip in Settings.front_end_ip_address:
            return func(*args, **kwargs)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied."
            )

    return wrapper


def is_valid_email(email):
    # Email validation regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    # Use the regex pattern to search for a match in the email string
    match = re.match(pattern, email)

    # If match is found, return True, else return False
    if match:
        return True
    else:
        return False


class GriffinMailService:

    def __init__(self):
        service_account_json_string = os.getenv("SERVICE_ACCOUNT_JSON")
        api_scope = ['https://mail.google.com']
        from_email = "no-reply@tradinglab.app"
        credentials = service_account.Credentials.from_service_account_info(
            info=json.loads(service_account_json_string),
            scopes=api_scope
        )
        delegated_credentials = credentials.with_subject(from_email)
        self.service = build('gmail', 'v1', credentials=delegated_credentials)

    def send(self, to, code):
        try:
            message = MIMEMultipart('alternative')
            message['From'] = os.getenv("EMAIL_FROM")
            message['To'] = to
            message['Subject'] = "Welcome to TradingLab"
            html = self.template(code, to)
            message.attach(MIMEText(html, 'html'))

            encoded_message = base64.urlsafe_b64encode(message.as_bytes())\
                .decode()
            msg = {
                'raw': encoded_message
            }

            self.service.users().messages().send(
                userId="me", body=msg
            ).execute()

            return True

        except HttpError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error.content
            )

    @staticmethod
    def template(activation_code: str, email: str):
        activation_link = f"""
            {os.getenv('FRONT_END_BASE_URL')}/activation?code={activation_code}
        """
        return f"""
          <!DOCTYPE HTML PUBLIC
            "-//W3C//DTD XHTML 1.0 Transitional //EN"
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
          <html
            xmlns="http://www.w3.org/1999/xhtml"
            xmlns:v="urn:schemas-microsoft-com:vml"
            xmlns:o="urn:schemas-microsoft-com:office:office"
          >
            <head>
              <!--[if gte mso 9]>
              <xml>
              <o:OfficeDocumentSettings>
              <o:AllowPNG/>
              <o:PixelsPerInch>96</o:PixelsPerInch>
              </o:OfficeDocumentSettings>
              </xml>
              <![endif]-->
              <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <meta name="x-apple-disable-message-reformatting">
              <!--[if !mso]><!--><meta http-equiv="X-UA-Compatible" content="IE=edge"><!--<![endif]-->
              <title></title>
              <link rel="stylesheet" type="text/css" href="https://storage.googleapis.com/tradinglab.app/css/email-style.css">
              <!--[if !mso]><!--><link href="https://fonts.googleapis.com/css2?family=Ubuntu:wght@300&display=swap" rel="stylesheet" type="text/css"><!--<![endif]-->
            </head>
            <body class="clean-body u_body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #3598db;color: #000000">
              <!--[if IE]><div class="ie-container"><![endif]-->
              <!--[if mso]><div class="mso-container"><![endif]-->
              <table id="u_body" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #3598db;width:100%" cellpadding="0" cellspacing="0">
                <tbody>
                  <tr style="vertical-align: top">
                    <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
                      <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="background-color: #3598db;"><![endif]-->
                      <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                          <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: transparent;"><![endif]-->

                            <!--[if (mso)|(IE)]><td align="center" width="600" class="v-col-padding" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
                            <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                              <div style="height: 100%;width: 100% !important;">
                                <!--[if (!mso)&(!IE)]><!--><div class="v-col-padding" style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;"><!--<![endif]-->

                                <table id="u_content_image_1" style="font-family:Ubuntu;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                  <tbody>
                                    <tr>
                                      <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:120px 10px 100px;font-family:Ubuntu;" align="left">

                                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                          <tr>
                                            <td class="v-text-align" style="padding-right: 0px;padding-left: 0px;" align="center">
                                              <img align="center" border="0" src="https://storage.googleapis.com/tradinglab.app/images/image-3.png" alt="Logo" title="Logo" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: inline-block !important;border: none;height: auto;float: none;width: 20%;max-width: 116px;" width="116" class="v-src-width v-src-max-width"/>
                                            </td>
                                          </tr>
                                        </table>
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                                <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
                              </div>
                            </div>
                            <!--[if (mso)|(IE)]></td><![endif]-->
                            <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                          </div>
                        </div>
                      </div>
                      <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                          <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: transparent;"><![endif]-->

                            <!--[if (mso)|(IE)]><td align="center" width="600" class="v-col-padding" style="background-color: #ecf0f1;width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                            <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                              <div style="background-color: #ecf0f1;height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                <!--[if (!mso)&(!IE)]><!--><div class="v-col-padding" style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                <table style="font-family:Ubuntu;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                  <tbody>
                                    <tr>
                                      <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:60px 10px 10px;font-family:Ubuntu;" align="left">

                                        <div class="v-text-align" style="font-size: 14px; line-height: 170%; text-align: center; word-wrap: break-word;">
                                          <p style="font-size: 14px; line-height: 170%;"><span style="font-size: 20px; line-height: 34px;"><strong><span style="line-height: 34px; font-size: 20px;">Hi there!</span></strong></span></p>
                                        </div>
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                                <table id="u_content_text_3" style="font-family:Ubuntu;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                  <tbody>
                                    <tr>
                                      <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px 100px 20px;font-family:Ubuntu;" align="left">

                                        <div class="v-text-align" style="font-size: 14px; line-height: 150%; text-align: center; word-wrap: break-word;">
                                          <p style="font-size: 14px; line-height: 150%;"><span style="font-size: 16px; line-height: 24px;">Please Verify that your email address is </span><span style="font-size: 16px; line-height: 24px;">{email} and that you entered it when </span><span style="font-size: 16px; line-height: 24px;">signing up for TradingLab.</span></p>
                                        </div>
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                                <table id="u_content_button_1" style="font-family:Ubuntu;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                  <tbody>
                                    <tr>
                                      <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:Ubuntu;" align="left">

                                        <div class="v-text-align" align="center">
                                          <!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://www.unlayer.com" style="height:39px; v-text-anchor:middle; width:290px;" arcsize="10.5%"  stroke="f" fillcolor="#3598db"><w:anchorlock/><center style="color:#FFFFFF;"><![endif]-->
                                          <a href="{activation_link}" target="_blank" class="v-button v-size-width" style="box-sizing: border-box;display: inline-block;text-decoration: none;-webkit-text-size-adjust: none;text-align: center;color: #FFFFFF; background-color: #3598db; border-radius: 4px;-webkit-border-radius: 4px; -moz-border-radius: 4px; width:50%; max-width:100%; overflow-wrap: break-word; word-break: break-word; word-wrap:break-word; mso-border-alt: none;font-size: 14px;">
                                            <span style="display:block;padding:10px 20px;line-height:120%;"><span style="font-size: 16px; line-height: 19.2px;"><strong><span style="line-height: 19.2px; font-size: 16px;">Verify Email</span></strong></span></span>
                                          </a>
                                          <!--[if mso]></center></v:roundrect><![endif]-->
                                        </div>
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                                <table id="u_content_text_2" style="font-family:Ubuntu;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                  <tbody>
                                    <tr>
                                      <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:20px 100px 60px;font-family:Ubuntu;" align="left">

                                        <div class="v-text-align" style="font-size: 14px; line-height: 170%; text-align: center; word-wrap: break-word;">
                                          <p style="font-size: 14px; line-height: 170%;">TradingLab is an automatic trading bot platform that empowers individuals to navigate the complex world of finance with confidence.</p>
                                        </div>
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                                <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
                              </div>
                            </div>
                            <!--[if (mso)|(IE)]></td><![endif]-->
                            <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                          </div>
                        </div>
                      </div>



                      <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                          <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: transparent;"><![endif]-->

                            <!--[if (mso)|(IE)]><td align="center" width="600" class="v-col-padding" style="background-color: #273b49;width: 600px;padding: 5px 80px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                            <div id="u_column_3" class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                              <div style="background-color: #273b49;height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                <!--[if (!mso)&(!IE)]><!--><div class="v-col-padding" style="box-sizing: border-box; height: 100%; padding: 5px 80px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                <table id="u_content_text_4" style="font-family:Ubuntu;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                  <tbody>
                                    <tr>
                                      <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:60px;font-family:Ubuntu;" align="left">

                                        <div class="v-text-align" style="font-size: 14px; color: #ffffff; line-height: 170%; text-align: center; word-wrap: break-word;">
                                          <p style="font-size: 14px; line-height: 170%;">Need help? <a rel="noopener" href="mailto:support@tradinglab.app?subject=Help%20on%20my%20TradingLab%20account" target="_blank">Contact our support team</a> or hit us on X <a rel="noopener" href="https://twitter.com/TradingLabXer" target="_blank">@TradingLabXer</a>. Want to give us feedback? Let us know what you think on our <a rel="noopener" href="https://tradinglab.app/contact-us" target="_blank">feedback site</a>.</p>
                                        </div>
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                                <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
                              </div>
                            </div>
                            <!--[if (mso)|(IE)]></td><![endif]-->
                            <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                          </div>
                        </div>
                      </div>



                      <!--[if gte mso 9]>
                      <table cellpadding="0" cellspacing="0" border="0" style="margin: 0 auto;min-width: 320px;max-width: 600px;">
                        <tr>
                          <td background="https://cdn.templates.unlayer.com/assets/1662456866997-back2.png" valign="top" width="100%">
                            <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="width: 600px;">
                            <v:fill type="frame" src="https://cdn.templates.unlayer.com/assets/1662456866997-back2.png" /><v:textbox style="mso-fit-shape-to-text:true" inset="0,0,0,0">
                            <![endif]-->

                            <div class="u-row-container" style="padding: 0px;background-color: transparent">
                              <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                                <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-image: url('https://storage.googleapis.com/tradinglab.app/images/image-2.png');background-repeat: no-repeat;background-position: center top;background-color: transparent;">
                                  <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-image: url('images/image-2.png');background-repeat: no-repeat;background-position: center top;background-color: transparent;"><![endif]-->

                                  <!--[if (mso)|(IE)]><td align="center" width="300" class="v-col-padding" style="background-color: #ecf0f1;width: 300px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                                  <div class="u-col u-col-50" style="max-width: 320px;min-width: 300px;display: table-cell;vertical-align: top;">
                                    <div style="background-color: #ecf0f1;height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                      <!--[if (!mso)&(!IE)]><!--><div class="v-col-padding" style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                      <table id="u_content_heading_3" style="font-family:Ubuntu;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                        <tbody>
                                          <tr>
                                            <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:25px 10px 0px 45px;font-family:Ubuntu;" align="left">

                                              <h1 class="v-text-align" style="margin: 0px; line-height: 140%; text-align: left; word-wrap: break-word; font-family: arial black,AvenirNext-Heavy,avant garde,arial; font-size: 22px; font-weight: 400;">TradingLab</h1>
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      <table id="u_content_social_1" class="hide-mobile" style="font-family:Ubuntu;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                        <tbody>
                                          <tr>
                                            <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px 10px 20px 48px;font-family:Ubuntu;" align="left">

                                              <div align="left">
                                                <div style="display: table; max-width:46px;">
                                                  <!--[if (mso)|(IE)]><table width="46" cellpadding="0" cellspacing="0" border="0"><tr><td style="border-collapse:collapse;" align="left"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse; mso-table-lspace: 0pt;mso-table-rspace: 0pt; width:46px;"><tr><![endif]-->


                                                  <!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 0px;" valign="top"><![endif]-->
                                                  <table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="width: 32px !important;height: 32px !important;display: inline-block;border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;margin-right: 0px">
                                                    <tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
                                                      <a href="https://x.com/TradingLabXer" title="X" target="_blank">
                                                        <img src="https://storage.googleapis.com/tradinglab.app/images/image-1.png" alt="X" title="X" width="26" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important">
                                                      </a>
                                                    </td></tr>
                                                  </tbody></table>
                                                  <!--[if (mso)|(IE)]></td><![endif]-->


                                                  <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                                                </div>
                                              </div>
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
                                    </div>
                                  </div>
                                  <!--[if (mso)|(IE)]></td><![endif]-->
                                  <!--[if (mso)|(IE)]><td align="center" width="300" class="v-col-padding" style="background-color: #ecf0f1;width: 300px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                                  <div class="u-col u-col-50" style="max-width: 320px;min-width: 300px;display: table-cell;vertical-align: top;">
                                    <div style="background-color: #ecf0f1;height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                      <!--[if (!mso)&(!IE)]><!--><div class="v-col-padding" style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                      <table id="u_content_text_5" style="font-family:Ubuntu;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                        <tbody>
                                          <tr>
                                            <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:31px 50px 30px 10px;font-family:Ubuntu;" align="left">

                                              <div class="v-text-align" style="font-size: 14px; line-height: 170%; text-align: right; word-wrap: break-word;">
                                                <p style="line-height: 170%;"><span style="font-size: 12px; line-height: 20.4px;">TradingLab is designed to help you build a strong portfolio with an ease in mind.</span></p>
                                              </div>
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
                                    </div>
                                  </div>
                                  <!--[if (mso)|(IE)]></td><![endif]-->
                                  <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                                </div>
                              </div>
                            </div>

                            <!--[if gte mso 9]>
                            </v:textbox></v:rect>
                          </td>
                        </tr>
                      </table>
                      <![endif]-->



                      <!--[if gte mso 9]>
                      <table cellpadding="0" cellspacing="0" border="0" style="margin: 0 auto;min-width: 320px;max-width: 600px;">
                        <tr>
                          <td background="https://cdn.templates.unlayer.com/assets/1662456713969-back2.png" valign="top" width="100%">
                            <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="width: 600px;">
                            <v:fill type="frame" src="https://cdn.templates.unlayer.com/assets/1662456713969-back2.png" /><v:textbox style="mso-fit-shape-to-text:true" inset="0,0,0,0">
                            <![endif]-->

                            <div class="u-row-container" style="padding: 0px;background-color: transparent">
                              <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                                <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-image: url('https://storage.googleapis.com/tradinglab.app/images/image-4.png');background-repeat: no-repeat;background-position: center top;background-color: transparent;">
                                  <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-image: url('images/image-4.png');background-repeat: no-repeat;background-position: center top;background-color: transparent;"><![endif]-->

                                  <!--[if (mso)|(IE)]><td align="center" width="600" class="v-col-padding" style="background-color: #273b49;width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                                  <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                                    <div style="background-color: #273b49;height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                      <!--[if (!mso)&(!IE)]><!--><div class="v-col-padding" style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                      <table style="font-family:Ubuntu;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                        <tbody>
                                          <tr>
                                            <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:20px;font-family:Ubuntu;" align="left">

                                              <div class="v-text-align" style="font-size: 14px; color: #ffffff; line-height: 140%; text-align: center; word-wrap: break-word;">
                                                <p style="font-size: 14px; line-height: 140%;">San Francisco, CA 94114</p>
                                              </div>
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
                                    </div>
                                  </div>
                                  <!--[if (mso)|(IE)]></td><![endif]-->
                                  <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                                </div>
                              </div>
                            </div>

                            <!--[if gte mso 9]>
                            </v:textbox></v:rect>
                          </td>
                        </tr>
                      </table>
                      <![endif]-->

                      <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
                    </td>
                  </tr>
                </tbody>
              </table>
              <!--[if mso]></div><![endif]-->
              <!--[if IE]></div><![endif]-->
            </body>
          </html>
        """
