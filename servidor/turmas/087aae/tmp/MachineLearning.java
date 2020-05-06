// -*- mode: java; c-basic-offset: 2; -*-
// Copyright 2020 MIT, All rights reserved
// Released under the Apache License, Version 2.0
// http://www.apache.org/licenses/LICENSE-2.0


package edu.mit.cne.appinventor;

import com.google.appinventor.components.annotations.DesignerComponent;
import com.google.appinventor.components.annotations.DesignerProperty;
import com.google.appinventor.components.annotations.PropertyCategory;
import com.google.appinventor.components.annotations.SimpleEvent;
import com.google.appinventor.components.annotations.SimpleFunction;
import com.google.appinventor.components.annotations.SimpleObject;
import com.google.appinventor.components.annotations.SimpleProperty;
import com.google.appinventor.components.annotations.UsesLibraries;
import com.google.appinventor.components.annotations.UsesPermissions;
import com.google.appinventor.components.common.ComponentCategory;
import com.google.appinventor.components.common.HtmlEntities;
import com.google.appinventor.components.common.PropertyTypeConstants;
import com.google.appinventor.components.common.YaVersion;
import com.google.appinventor.components.runtime.AndroidNonvisibleComponent;
import com.google.appinventor.components.runtime.Component;
import com.google.appinventor.components.runtime.ComponentContainer;
import com.google.appinventor.components.runtime.EventDispatcher;
import com.google.appinventor.components.runtime.HandlesEventDispatching;
import com.google.appinventor.components.runtime.Web;
import com.google.appinventor.components.runtime.collect.Lists;
import com.google.appinventor.components.runtime.collect.Maps;
import com.google.appinventor.components.runtime.util.AsynchUtil;
import com.google.appinventor.components.runtime.util.ErrorMessages;
import com.google.appinventor.components.runtime.util.FileUtil;
import com.google.appinventor.components.runtime.util.GingerbreadUtil;
import com.google.appinventor.components.runtime.util.JsonUtil;
import com.google.appinventor.components.runtime.util.MediaUtil;
import com.google.appinventor.components.runtime.util.SdkLevel;
import com.google.appinventor.components.runtime.util.YailList;

import android.app.Activity;
import android.text.TextUtils;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;
import org.json.XML;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.CookieHandler;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URISyntaxException;
import java.net.URL;
import java.net.URLEncoder;
import java.util.List;
import java.util.Map;

@DesignerComponent(
	  version = YaVersion.WEB_COMPONENT_VERSION, 
	  description = "Descrição",
	  category = ComponentCategory.EXTENSION,
	  nonVisible = true, 
	  iconName = "images/extension.png")
@SimpleObject(external = true)
@UsesPermissions(
	  permissionNames = "android.permission.INTERNET," + 
			  "android.permission.WRITE_EXTERNAL_STORAGE," +
			  "android.permission.READ_EXTERNAL_STORAGE")
@UsesLibraries(libraries = "json.jar")

public class MachineLearning extends AndroidNonvisibleComponent implements Component {

    private static final String LOG_TAG = "Machine Learning Extension";
	private final Activity activity;
	private boolean saveResponse = true;
	private YailList requestHeaders = new YailList();

	private String enderecoServidor = "http://localhost:5000/";
	private String tagTurma = "";

    private String urlString = "";
	private String classificacao = "";
	private Byte[] image = null;

	private static class CapturedProperties {
        final String urlString;
        final URL url;
	    final String classificacao;
	    final Byte[] image;
	    final boolean saveResponse;
		final Map<String, List<String>> requestHeaders;

		CapturedProperties(MachineLearning machineLearning) throws MalformedURLException, InvalidRequestHeadersException {
            urlString = machineLearning.urlString;
            url = new URL(urlString);
	        classificacao = machineLearning.classificacao;
	        image = machineLearning.image;
	        saveResponse = machineLearning.saveResponse;
		    requestHeaders = processRequestHeaders(machineLearning.requestHeaders);
		}
	}

	public MachineLearning(ComponentContainer container) {
		super(container.$form());
		activity = container.$context();
	}

    // TODO:: Set Endereco Servidor Default value
	@DesignerProperty(editorType = PropertyTypeConstants.PROPERTY_TYPE_STRING, defaultValue = "")
	@SimpleProperty(description = "desription")
	public void EnderecoServidor(String enderecoServidor) {
		if (enderecoServidor != null) {
			this.enderecoServidor = enderecoServidor.trim();
		}
	}

	@DesignerProperty(editorType = PropertyTypeConstants.PROPERTY_TYPE_STRING, defaultValue = "")
	@SimpleProperty(description = "desription")
	public void TagTurma(String tagTurma) {
		if (tagTurma != null) {
			this.tagTurma = tagTurma.trim();
		}
	}

	@SimpleFunction(description = "desription")
	public void Classificar() {
		// TODO:: Change URL
		String url = this.enderecoServidor + "/classificar";
		final CapturedProperties webProps = capturePropertyValues("MachineLearning");

		// TODO:: Check for null?
		if (this.enderecoServidor.isEmpty() || this.tagTurma.isEmpty()) {
			return;
		}

		AsynchUtil.runAsynchronously(new Runnable() {
			@Override
			public void run() {
				try {
					performRequest(webProps, null, null, "CLASSIFICAR");
				} catch (FileUtil.FileException e) {
					form.dispatchErrorOccurredEvent(MachineLearning.this, "Classificar", e.getErrorMessageNumber());
				} catch (Exception e) {
					Log.e(LOG_TAG, "ERROR_UNABLE_TO_GET", e);
					form.dispatchErrorOccurredEvent(MachineLearning.this, "Classificar", ErrorMessages.ERROR_WEB_UNABLE_TO_GET, webProps.urlString);
				}
			}
		});
	}

    private void performRequest(final CapturedProperties webProps, byte[] postData, String postFile, String httpVerb) throws IOException {
		HttpURLConnection connection = openConnection(webProps, httpVerb);
		if (connection != null) {
			try {
				if (postData != null) {
					writeRequestData(connection, postData);
				} else if (postFile != null) {
					writeRequestFile(connection, postFile);
				}

				// Get the response.
				final int responseCode = connection.getResponseCode();
				final String responseType = getResponseType(connection);

				if (!saveResponse) {
					final String classificacao = getResponseContent(connection);

					// Dispatch the event.
					activity.runOnUiThread(new Runnable() {
						@Override
						public void run() {
							ClassificarImagem(classificacao);
						}
					});
				}

			} finally {
				connection.disconnect();
			}
		}
	}

	@SimpleEvent(description = "desription")
	public void ClassificarImagem(String classificacao) {
		EventDispatcher.dispatchEvent(this, "Capturar", "", 200, "JSON", classificacao);
	}


	private static HttpURLConnection openConnection(CapturedProperties webProps, String httpVerb) throws IOException, ClassCastException, ProtocolException {
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
		return connection;
	}

	private static void writeRequestData(HttpURLConnection connection, byte[] postData) throws IOException {
		connection.setDoOutput(true);
		connection.setFixedLengthStreamingMode(postData.length);
		BufferedOutputStream out = new BufferedOutputStream(connection.getOutputStream());
		try {
			out.write(postData, 0, postData.length);
			out.flush();
		} finally {
			out.close();
		}
	}

	private void writeRequestFile(HttpURLConnection connection, String path) throws IOException {
		BufferedInputStream in = new BufferedInputStream(MediaUtil.openMedia(form, path));
		try {
			connection.setDoOutput(true); 
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

	private static String getResponseType(HttpURLConnection connection) {
		String responseType = connection.getContentType();
		return (responseType != null) ? responseType : "";
	}

	private static String getResponseContent(HttpURLConnection connection) throws IOException {
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

	private static String saveResponseContent(HttpURLConnection connection, String responseFileName, String responseType) throws IOException {
		File file = createFile(responseFileName, responseType);
		BufferedInputStream in = new BufferedInputStream(getConnectionStream(connection), 0x1000);
		try {
			BufferedOutputStream out = new BufferedOutputStream(new FileOutputStream(file), 0x1000);
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

		return file.getAbsolutePath();
	}

	private static InputStream getConnectionStream(HttpURLConnection connection) {
		try {
			return connection.getInputStream();
		} catch (IOException e1) {
			return connection.getErrorStream();
		}
	}

	private static File createFile(String fileName, String responseType) throws IOException, FileUtil.FileException {
		if (!TextUtils.isEmpty(fileName)) {
			return FileUtil.getExternalFile(fileName);
		}

		int indexOfSemicolon = responseType.indexOf(';');
		if (indexOfSemicolon != -1) {
			responseType = responseType.substring(0, indexOfSemicolon);
		}
		String extension = mimeTypeToExtension.get(responseType);
		if (extension == null) {
			extension = "tmp";
		}
		return FileUtil.getDownloadFile(extension);
	}

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

	private CapturedProperties capturePropertyValues(String functionName) {
		try {
			return new CapturedProperties(this);
		} catch (MalformedURLException e) {
			form.dispatchErrorOccurredEvent(this, functionName, ErrorMessages.ERROR_WEB_MALFORMED_URL, this.urlString);
		} catch (InvalidRequestHeadersException e) {
			form.dispatchErrorOccurredEvent(this, functionName, e.errorNumber, e.index);
		}
		return null;
	}

	private static class InvalidRequestHeadersException extends Exception {
		final int errorNumber;
		final int index;

		InvalidRequestHeadersException(int errorNumber, int index) {
			super();
			this.errorNumber = errorNumber;
			this.index = index;
		}
	}

	private static class BuildRequestDataException extends Exception {
		final int errorNumber;
		final int index;

		BuildRequestDataException(int errorNumber, int index) {
			super();
			this.errorNumber = errorNumber;
			this.index = index;
		}
	}

	private static final Map<String, String> mimeTypeToExtension;
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

