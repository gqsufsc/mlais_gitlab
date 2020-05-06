// -*- mode: java; c-basic-offset: 2; -*-
// Copyright 2009-2011 Google, All Rights reserved
// Copyright 2011-2012 MIT, All rights reserved
// Released under the Apache License, Version 2.0
// http://www.apache.org/licenses/LICENSE-2.0

package edu.mit.cne.appinventor.ML;
//package com.google.appinventor.components.runtime;

import com.google.appinventor.components.annotations.DesignerComponent;
import com.google.appinventor.components.annotations.DesignerProperty;
import com.google.appinventor.components.annotations.SimpleEvent;
import com.google.appinventor.components.annotations.SimpleFunction;
import com.google.appinventor.components.annotations.SimpleObject;
import com.google.appinventor.components.annotations.SimpleProperty;
import com.google.appinventor.components.annotations.UsesLibraries;
import com.google.appinventor.components.annotations.UsesPermissions;
import com.google.appinventor.components.common.ComponentCategory;
import com.google.appinventor.components.common.PropertyTypeConstants;
import com.google.appinventor.components.common.YaVersion;
import com.google.appinventor.components.runtime.AndroidNonvisibleComponent;
import com.google.appinventor.components.runtime.Component;
import com.google.appinventor.components.runtime.ComponentContainer;
import com.google.appinventor.components.runtime.EventDispatcher;
import com.google.appinventor.components.runtime.collect.Lists;
import com.google.appinventor.components.runtime.collect.Maps;
import com.google.appinventor.components.runtime.errors.PermissionException;
import com.google.appinventor.components.runtime.errors.RequestTimeoutException;
import com.google.appinventor.components.runtime.util.AsynchUtil;
import com.google.appinventor.components.runtime.util.ErrorMessages;
import com.google.appinventor.components.runtime.util.FileUtil;
import com.google.appinventor.components.runtime.util.GingerbreadUtil;
import com.google.appinventor.components.runtime.util.JsonUtil;
import com.google.appinventor.components.runtime.util.MediaUtil;
import com.google.appinventor.components.runtime.util.SdkLevel;
import com.google.appinventor.components.runtime.util.YailDictionary;
import com.google.appinventor.components.runtime.util.YailList;

import android.app.Activity;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.CookieHandler;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.SocketTimeoutException;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.AbstractMap;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

@DesignerComponent(
		version = YaVersion.WEB_COMPONENT_VERSION, 
		description = "", 
		category = ComponentCategory.EXTENSION, 
		nonVisible = true,
		iconName = "images/extension.png")
@SimpleObject(external = true)
@UsesPermissions(
		permissionNames = "android.permission.INTERNET," 
				+ "android.permission.WRITE_EXTERNAL_STORAGE,"
				+ "android.permission.READ_EXTERNAL_STORAGE")
@UsesLibraries(libraries = "json.jar")

public class ML extends AndroidNonvisibleComponent implements Component {
	
	private final String UPLOAD = "Upload";
	private final String PREDICT = "Classificar";
	
	private final String RESPONSE_ERROR = "error";
	private final String RESPONSE_STATUS = "status";
	private final String RESPONSE_PREDICT = "result";

	// Our attrs
	private String enderecoServidor = "";
	private String tagTurma = "";
	private String imagePath = "";
	
	// Decoded JSON reply
	private static String error;
	private static String status;
	private static String predict;
	
	// Web component
	private String urlString;
	private boolean allowCookies;
    final YailList requestHeaders  = new YailList();
	
	// Other Attrs
	private static final Map<String, String> mimeTypeToExtension;
	private final Activity activity;
	private final CookieHandler cookieHandler;
	
	// Altered from from Web component
	private static class CapturedProperties {
		final String imagem;
		final String urlString;
		final URL url;
		final boolean allowCookies;
		final Map<String, List<String>> requestHeaders;
		final Map<String, List<String>> cookies;

		CapturedProperties(ML ml) throws MalformedURLException, InvalidRequestHeadersException {
			imagem = ml.imagePath;
			urlString = ml.urlString;
			url = new URL(urlString);
			allowCookies = ml.allowCookies;
			requestHeaders = processRequestHeaders(ml.requestHeaders);
			
			Map<String, List<String>> cookiesTemp = null;
			if (allowCookies && ml.cookieHandler != null) {
				try {
					cookiesTemp = ml.cookieHandler.get(url.toURI(), requestHeaders);
				} catch (URISyntaxException e) {
					// Can't convert the URL to a URI; no cookies for you.
				} catch (IOException e) {
					// Sorry, no cookies for you.
				}
			}
			cookies = cookiesTemp;
		}
	}

	public ML(ComponentContainer container) {
		super(container.$form());
		activity = container.$context();
		cookieHandler = (SdkLevel.getLevel() >= SdkLevel.LEVEL_GINGERBREAD) ? GingerbreadUtil.newCookieManager() : null;
	}

	// Setter
	@DesignerProperty(editorType = PropertyTypeConstants.PROPERTY_TYPE_STRING, defaultValue = "192.168.100.10:5000")
	@SimpleProperty
	public void EnderecoServidor(String enderecoServidor) {
		if (enderecoServidor != null) {
			this.enderecoServidor = enderecoServidor.trim();
		}
	}
	
	// Getter
	@SimpleProperty
	public String EnderecoServidor() {
		return this.enderecoServidor != null ? enderecoServidor : "";
	}

	// Setter
	@DesignerProperty(editorType = PropertyTypeConstants.PROPERTY_TYPE_STRING, defaultValue = "087aae")
	@SimpleProperty
	public void TagTurma(String tagTurma) {
		if (tagTurma != null) {
			this.tagTurma = tagTurma.trim();
		}
	}
	
	// Getter
	@SimpleProperty
	public String TagTurma() {
		return tagTurma != null? tagTurma : "";
	}
	
	@SimpleProperty(description = "description")
	public void Imagem(String imagePath) {
		if (imagePath != null) {
			this.imagePath = imagePath.trim();
		}
	}
	
	// Getter
	@SimpleProperty
	public String Imagem() {
		return imagePath != null ? imagePath : "";
	}

	@SimpleFunction
	public void UploadImage() {
		clearResponseStrings();
	    this.urlString = "http://" + this.enderecoServidor + "/upload/" + this.tagTurma;
	    
        // Capture property values before running asynchronously.
        final CapturedProperties webProps = capturePropertyValues(UPLOAD);
        if (webProps == null) {
        	// capturePropertyValues has already called form.dispatchErrorOccurredEvent
        	return;
        }

        AsynchUtil.runAsynchronously(new Runnable() {
        	@Override
        	public void run() {
	            try {
	            	performRequest(webProps, null, webProps.imagem, "POST", UPLOAD);
	            } catch (PermissionException e) {
	            	form.dispatchPermissionDeniedEvent(ML.this, UPLOAD, e);
	            } catch (FileUtil.FileException e) {
	            	form.dispatchErrorOccurredEvent(ML.this, UPLOAD, e.getErrorMessageNumber());
	            } catch (RequestTimeoutException e) {
	            	form.dispatchErrorOccurredEvent(ML.this, UPLOAD, ErrorMessages.ERROR_WEB_REQUEST_TIMED_OUT, webProps.urlString);
	            } catch (Exception e) {
	            	form.dispatchErrorOccurredEvent(ML.this, UPLOAD, ErrorMessages.ERROR_WEB_UNABLE_TO_POST_OR_PUT_FILE, webProps.imagem, webProps.urlString);
	            }
        	}
        });
	}
	
	@SimpleFunction
	public void Classificar() {
		clearResponseStrings();
		this.urlString = "http://" + this.enderecoServidor + "/predict/" + this.tagTurma;

        // Capture property values before running asynchronously.
        final CapturedProperties webProps = capturePropertyValues(PREDICT);
        if (webProps == null) {
          // capturePropertyValues has already called form.dispatchErrorOccurredEvent
          return;
        }

        AsynchUtil.runAsynchronously(new Runnable() {
        	@Override
        	public void run() {
            try {
	              performRequest(webProps, null, webProps.imagem, "POST", PREDICT);
	            } catch (PermissionException e) {
	              form.dispatchPermissionDeniedEvent(ML.this, PREDICT, e);
	            } catch (FileUtil.FileException e) {
	              form.dispatchErrorOccurredEvent(ML.this, PREDICT,
	                  e.getErrorMessageNumber());
	            } catch (RequestTimeoutException e) {
	              form.dispatchErrorOccurredEvent(ML.this, PREDICT,
	                  ErrorMessages.ERROR_WEB_REQUEST_TIMED_OUT, webProps.urlString);
	            } catch (Exception e) {
	              form.dispatchErrorOccurredEvent(ML.this, PREDICT,
	                  ErrorMessages.ERROR_WEB_UNABLE_TO_POST_OR_PUT_FILE, webProps.imagem, webProps.urlString);
	            }
        	}
        });
	}
	
	private void decodeJson(String json) {
		YailDictionary response = (YailDictionary) JsonUtil.getObjectFromJson(json, Boolean.TRUE);
		if (response.containsKey(RESPONSE_ERROR)) {
			error = (String) response.get(RESPONSE_ERROR);
		} else if (response.containsKey(RESPONSE_STATUS)) {
			status = (String) response.get(RESPONSE_STATUS);
		} else if (response.containsKey(RESPONSE_PREDICT)) {
			predict = (String) response.get(RESPONSE_PREDICT);
		}
	}
	
	private void clearResponseStrings() {
		error = "";
		status = "";
		predict = "";
	}
	
	public static String getError() {
		return error;
	}
	
	public static String getStatus() {
		return status;
	}
	
	public static String getPredict() {
		return predict;
	}
	
		
	@SimpleEvent
	public void Upload(String status, String error) {
		EventDispatcher.dispatchEvent(this, "Upload", status, error);
	}
	
	@SimpleEvent
	public void Classify(String classification, String error) {
		EventDispatcher.dispatchEvent(this, "Classify", classification, error);
	}
	
	@SimpleEvent
	public void TimedOut(String url) {
		EventDispatcher.dispatchEvent(this, "TimedOut", url);
	}
	
	// Derived from Web component
	private void performRequest(final CapturedProperties webProps, byte[] postData, String postFile, String httpVerb, String method) 
			throws RequestTimeoutException, IOException {
		HttpURLConnection connection = openConnection(webProps, httpVerb);
		
		// Adding extension type to requestHeader
		int index = this.imagePath.lastIndexOf('.');
	    String extension = index == -1 ? "" : this.imagePath.substring(index + 1);
		if (extension != "") {
			connection.addRequestProperty("extension", extension);
		}
		
		if (connection != null) {
			try {
				if (postData != null) {
					writeRequestData(connection, postData);
		        } else if (postFile != null) {
		        	writeRequestFile(connection, postFile);
		        }
				
		        // Get the response.
//		        final int responseCode = connection.getResponseCode();
//		        final String responseType = getResponseType(connection);
		        final String responseContent = getResponseContent(connection);
		        decodeJson(responseContent);
		        
				if (method == UPLOAD) {
					// Dispatch the event.
					activity.runOnUiThread(new Runnable() {
						@Override
			            public void run() {
							Upload(ML.getStatus(), ML.getError());
						}
					});
				} else if (method == PREDICT) {
					// Dispatch the event.
					activity.runOnUiThread(new Runnable() {
						@Override
			            public void run() {
							Classify(ML.getPredict(), ML.getError());
						}
					});
				}
			} catch (SocketTimeoutException e) {
		        // Dispatch timeout event.
		        activity.runOnUiThread(new Runnable() {
		        	@Override
		        	public void run() {
		        		TimedOut(webProps.urlString);
		        	}
		        });
		        throw new RequestTimeoutException();
			} finally {
				connection.disconnect();
			}
		}
	}

	// From web component
	private static HttpURLConnection openConnection(CapturedProperties webProps, String httpVerb)
			throws IOException, ClassCastException, ProtocolException {

		HttpURLConnection connection = (HttpURLConnection) webProps.url.openConnection();

		if (httpVerb.equals("PUT") || httpVerb.equals("DELETE")) {
			connection.setRequestMethod(httpVerb);
		}

		// Request Headers
		for (Map.Entry<String, List<String>> header : webProps.requestHeaders.entrySet()) {
			String name = header.getKey();
			for (String value : header.getValue()) {
				connection.addRequestProperty(name, value);
			}
		}

		// Cookies
		if (webProps.cookies != null) {
			for (Map.Entry<String, List<String>> cookie : webProps.cookies.entrySet()) {
				String name = cookie.getKey();
				for (String value : cookie.getValue()) {
					connection.addRequestProperty(name, value);
				}
			}
		}
		return connection;
	}

	// From web component
	private static void writeRequestData(HttpURLConnection connection, byte[] postData) throws IOException {
		connection.setDoOutput(true); // This makes it something other than a HTTP GET.
		connection.setFixedLengthStreamingMode(postData.length);
		BufferedOutputStream out = new BufferedOutputStream(connection.getOutputStream());
		try {
			out.write(postData, 0, postData.length);
			out.flush();
		} finally {
			out.close();
		}
	}

	// From web compoent
	private void writeRequestFile(HttpURLConnection connection, String path) throws IOException {
		BufferedInputStream in = new BufferedInputStream(MediaUtil.openMedia(form, path));
		try {
			connection.setDoOutput(true); // This makes it something other than a HTTP GET.
			connection.setChunkedStreamingMode(0);
			BufferedOutputStream out = new BufferedOutputStream(connection.getOutputStream());
			try {
				while (true) {
					int b = in.read();
					if (b == -1) {
						break;
					}
					out.write(b);
				}
				out.flush();
			} finally {
				out.close();
			}
		} finally {
			in.close();
		}
	}

	// From web compoent
	private static String getResponseType(HttpURLConnection connection) {
		String responseType = connection.getContentType();
		return (responseType != null) ? responseType : "";
	}

	// From web compoent
	private static String getResponseContent(HttpURLConnection connection) throws IOException {
		// Use the content encoding to convert bytes to characters.
		String encoding = connection.getContentEncoding();
		if (encoding == null) {
			encoding = "UTF-8";
		}
		InputStreamReader reader = new InputStreamReader(getConnectionStream(connection), encoding);
		try {
			int contentLength = connection.getContentLength();
			StringBuilder sb = (contentLength != -1) ? new StringBuilder(contentLength) : new StringBuilder();
			char[] buf = new char[1024];
			int read;
			while ((read = reader.read(buf)) != -1) {
				sb.append(buf, 0, read);
			}
			return sb.toString();
		} finally {
			reader.close();
		}
	}
	
	// From web compoent
	private static InputStream getConnectionStream(HttpURLConnection connection) {
		try {
			return connection.getInputStream();
		} catch (IOException e1) {
			return connection.getErrorStream();
		}
	}

	// From web component
	private static Map<String, List<String>> processRequestHeaders(YailList list) throws InvalidRequestHeadersException {
		Map<String, List<String>> requestHeadersMap = Maps.newHashMap();
		for (int i = 0; i < list.size(); i++) {
			Object item = list.getObject(i);
			if (item instanceof YailList) {
				YailList sublist = (YailList) item;
				if (sublist.size() == 2) {
					String fieldName = sublist.getObject(0).toString();
					Object fieldValues = sublist.getObject(1);

					String key = fieldName;
					List<String> values = Lists.newArrayList();
					if (fieldValues instanceof YailList) {
						YailList multipleFieldsValues = (YailList) fieldValues;
						for (int j = 0; j < multipleFieldsValues.size(); j++) {
							Object value = multipleFieldsValues.getObject(j);
							values.add(value.toString());
						}
					} else {
						Object singleFieldValue = fieldValues;
						values.add(singleFieldValue.toString());
					}
					requestHeadersMap.put(key, values);
				} else {
					throw new InvalidRequestHeadersException(ErrorMessages.ERROR_WEB_REQUEST_HEADER_NOT_TWO_ELEMENTS, i + 1);
				}
			} else {
				throw new InvalidRequestHeadersException(ErrorMessages.ERROR_WEB_REQUEST_HEADER_NOT_LIST, i + 1);
			}
		}
		return requestHeadersMap;
	}

	// From web component
	private CapturedProperties capturePropertyValues(String functionName) {
		try {
			return new CapturedProperties(this);
		} catch (MalformedURLException e) {
			form.dispatchErrorOccurredEvent(this, functionName, ErrorMessages.ERROR_WEB_MALFORMED_URL, urlString);
		} catch (InvalidRequestHeadersException e) {
			form.dispatchErrorOccurredEvent(this, functionName, e.errorNumber, e.index);
		}
		return null;
	}
	
	// From web component
	@SuppressWarnings("serial")
	private static class InvalidRequestHeadersException extends Exception {
		final int errorNumber;
		final int index; // the index of the invalid header

		InvalidRequestHeadersException(int errorNumber, int index) {
			super();
			this.errorNumber = errorNumber;
			this.index = index;
		}
	}

	// From web component
	// VisibleForTesting
	@SuppressWarnings("serial")
	static class BuildRequestDataException extends Exception {
		final int errorNumber;
		final int index; // the index of the invalid header

		BuildRequestDataException(int errorNumber, int index) {
			super();
			this.errorNumber = errorNumber;
			this.index = index;
		}
	}

	// From web component
	static {
		mimeTypeToExtension = Maps.newHashMap();
		mimeTypeToExtension.put("application/pdf", "pdf");
		mimeTypeToExtension.put("application/zip", "zip");
		mimeTypeToExtension.put("audio/mpeg", "mpeg");
		mimeTypeToExtension.put("audio/mp3", "mp3");
		mimeTypeToExtension.put("audio/mp4", "mp4");
		mimeTypeToExtension.put("image/gif", "gif");
		mimeTypeToExtension.put("image/jpeg", "jpg");
		mimeTypeToExtension.put("image/png", "png");
		mimeTypeToExtension.put("image/tiff", "tiff");
		mimeTypeToExtension.put("text/plain", "txt");
		mimeTypeToExtension.put("text/html", "html");
		mimeTypeToExtension.put("text/xml", "xml");
	}
}