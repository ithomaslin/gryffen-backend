import re
import os
import base64
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from functools import wraps
from fastapi import Request, HTTPException, status

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
        base_directory = os.path.dirname(os.path.abspath(__file__))
        credential_filepath = os.path.join(
            base_directory, os.getenv("SERVICE_ACCOUNT_KEY")
        )
        api_scope = ['https://mail.google.com']
        from_email = 'griffin@neat.tw'
        credentials = service_account.Credentials.from_service_account_file(
            credential_filepath, scopes=api_scope)
        delegated_credentials = credentials.with_subject(from_email)
        self.service = build('gmail', 'v1', credentials=delegated_credentials)

    def send(self, to, code):
        try:
            message = MIMEMultipart('alternative')
            message['From'] = os.getenv("EMAIL_FROM")
            message['To'] = to
            message['Subject'] = "Thank you for choosing Griffin."
            html = self.template(code, to)
            message.attach(MIMEText(html, 'html'))

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            msg = {
                'raw': encoded_message
            }

            self.service.users().messages().send(
                userId="me", body=msg
            ).execute()

        except HttpError as error:
            print(error)

    @staticmethod
    def template(activation_code: str, email: str):
        activation_link = f"{os.getenv('FRONT_END_BASE_URL')}/activation?code={activation_code}"
        ldap = email.split("@")[0]
        return f"""
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            <html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
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
                <!--[if !mso]><!-->
                <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700&display=swap" rel="stylesheet" type="text/css">
                <!--<![endif]-->
              </head>
              <body class="clean-body u_body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #000000;color: #000000">
                <!--[if IE]><div class="ie-container"><![endif]-->
                <!--[if mso]><div class="mso-container"><![endif]-->
                <table id="u_body" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #000000;width:100%" cellpadding="0" cellspacing="0">
                  <tbody>
                    <tr style="vertical-align: top">
                      <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
                        <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="background-color: #000000;"><![endif]-->

                        <div class="u-row-container" style="padding: 0px;background-color: transparent">
                          <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                            <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                              <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: transparent;"><![endif]-->

                              <!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
                              <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                                <div style="height: 100%;width: 100% !important;">
                                  <!--[if (!mso)&(!IE)]><!--><div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;"><!--<![endif]-->

                                  <table id="u_content_image_1" style="font-family:'Open Sans',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                      <tr>
                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:120px 10px 100px;font-family:'Open Sans',sans-serif;" align="left">

                                          <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                            <tr>
                                              <td style="padding-right: 0px;padding-left: 0px;" align="center">

                                                <img align="center" border="0" src="images/image-1.png" alt="Logo" title="Logo" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: inline-block !important;border: none;height: auto;float: none;width: 47%;max-width: 272.6px;" width="272.6" class="v-src-width v-src-max-width"/>

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
                          <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                            <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-image: url('images/image-2.png');background-repeat: no-repeat;background-position: center top;background-color: transparent;">
                              <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-image: url('images/image-2.png');background-repeat: no-repeat;background-position: center top;background-color: transparent;"><![endif]-->

                              <!--[if (mso)|(IE)]><td align="center" width="600" style="background-color: #ffffff;width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                              <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                                <div style="background-color: #ffffff;height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                  <!--[if (!mso)&(!IE)]><!--><div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                  <table style="font-family:'Open Sans',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                      <tr>
                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:60px 10px 10px;font-family:'Open Sans',sans-serif;" align="left">

                                          <div style="font-size: 14px; line-height: 170%; text-align: center; word-wrap: break-word;">
                                            <p style="font-size: 14px; line-height: 170%;"><span style="font-size: 20px; line-height: 34px;"><strong><span style="line-height: 34px; font-size: 20px;">Hi {ldap},</span></strong></span></p>
                                          </div>
                                        </td>
                                      </tr>
                                    </tbody>
                                  </table>
                                  <table id="u_content_text_3" style="font-family:'Open Sans',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                      <tr>
                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px 100px 20px;font-family:'Open Sans',sans-serif;" align="left">

                                          <div style="font-size: 14px; line-height: 170%; text-align: center; word-wrap: break-word;">
                                            <p style="font-size: 14px; line-height: 170%;"><span style="font-size: 16px; line-height: 27.2px;">Please Verify that your email address is </span><span style="font-size: 16px; line-height: 27.2px;">{email} and that you entered it when </span><span style="font-size: 16px; line-height: 27.2px;">signing up for Griffin.</span></p>
                                          </div>
                                        </td>
                                      </tr>
                                    </tbody>
                                  </table>
                                  <table id="u_content_button_1" style="font-family:'Open Sans',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                      <tr>
                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Open Sans',sans-serif;" align="left">

                                          <div align="center">
                                            <!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://www.unlayer.com" style="height:39px; v-text-anchor:middle; width:290px;" arcsize="10.5%"  stroke="f" fillcolor="#f14b23"><w:anchorlock/><center style="color:#FFFFFF;font-family:'Open Sans',sans-serif;"><![endif]-->
                                            <a href="{activation_link}" target="_blank" class="v-button v-size-width" style="box-sizing: border-box;display: inline-block;font-family:'Open Sans',sans-serif;text-decoration: none;-webkit-text-size-adjust: none;text-align: center;color: #FFFFFF; background-color: #f14b23; border-radius: 4px;-webkit-border-radius: 4px; -moz-border-radius: 4px; width:50%; max-width:100%; overflow-wrap: break-word; word-break: break-word; word-wrap:break-word; mso-border-alt: none;font-size: 14px;">
                                              <span style="display:block;padding:10px 20px;line-height:120%;"><span style="font-size: 16px; line-height: 19.2px;"><strong><span style="line-height: 19.2px; font-size: 16px;">Verify Email</span></strong></span></span>
                                            </a>
                                            <!--[if mso]></center></v:roundrect><![endif]-->
                                          </div>
                                        </td>
                                      </tr>
                                    </tbody>
                                  </table>
                                  <table id="u_content_text_2" style="font-family:'Open Sans',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                      <tr>
                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:20px 100px 60px;font-family:'Open Sans',sans-serif;" align="left">

                                          <div style="font-size: 14px; line-height: 170%; text-align: center; word-wrap: break-word;">
                                            <p style="line-height: 170%;">Griffin is an automated trading platform that enables users to execute trades through algorithmic strategies. It allows users to access real-time market data, create and customize trading strategies, and manage their positions.</p>
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
                          <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                            <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                              <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: transparent;"><![endif]-->

                              <!--[if (mso)|(IE)]><td align="center" width="600" style="background-color: #000000;width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                              <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                                <div style="background-color: #000000;height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                  <!--[if (!mso)&(!IE)]><!--><div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                  <table id="u_content_text_4" style="font-family:'Open Sans',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                      <tr>
                                        <td class="v-container-padding-padding" style="overflow-wrap:break-word;word-break:break-word;padding:60px 80px;font-family:'Open Sans',sans-serif;" align="left">

                                          <div style="font-size: 14px; color: #ffffff; line-height: 170%; text-align: center; word-wrap: break-word;">
                                            <p style="font-size: 14px; line-height: 170%;">Need help? <a rel="noopener" href="https://www.unlayer.com" target="_blank" style="color: #f1c40f;">Contact our support team</a>. Want to give us feedback? Let us know what you think on our <a rel="noopener" href="https://www.unlayer.com" target="_blank" style="color: #f1c40f;">feedback site</a>.</p>
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
