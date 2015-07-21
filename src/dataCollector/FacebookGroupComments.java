package dataCollector;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;

import javax.json.Json;
import javax.json.JsonArray;
import javax.json.JsonObject;
import javax.json.JsonReader;

public class FacebookGroupComments {

	/**
	 * Take the Json object and extract the content we want to write into the file
	 * @param myObj
	 * @return
	 */
	public static String createWritable(JsonObject myObj){
		return myObj.getString("id") + "\t" + myObj.getJsonObject("from").getString("id")
		+ "\t" + myObj.getString("created_time") + "\t" + myObj.getString("message") + "\n";
		
	}
	
	public static void fetchGroupComments(String pageID, String folderPath, String token) throws IOException {

		String outFileName = pageID + "_comments.txt";

		URL url = new URL("https://graph.facebook.com/" + pageID + "/posts?access_token=" + token);
		System.setProperty("https.proxyHost", "proxy.iiit.ac.in");
		System.setProperty("https.proxyPort", "8080");

		BufferedWriter bw = new BufferedWriter(new FileWriter(folderPath + "/" + outFileName));

		System.out.println("Crawling FB Data...");
		
		try (InputStream is = url.openStream(); JsonReader rdr = Json.createReader(is)) {
			JsonObject obj = rdr.readObject();
			JsonArray results = obj.getJsonArray("data");
			
			for (JsonObject result : results.getValuesAs(JsonObject.class)) {
				if (result.getJsonObject("comments") == null)
					continue;
				JsonObject js_nested = result.getJsonObject("comments");
				JsonArray results1 = js_nested.getJsonArray("data");
				for (JsonObject result1 : results1.getValuesAs(JsonObject.class)) {
					String writable = createWritable(result1);
					System.out.println(writable);
					bw.write(writable);
				}
				try {
					if (js_nested.containsKey("paging")) {
						while (js_nested.getJsonObject("paging").containsKey("next")) {
							URL url_after = new URL(js_nested.getJsonObject("paging").getString("next"));
							try (InputStream is_after = url_after.openStream();
									JsonReader rdr_after = Json.createReader(is_after)) {

								js_nested = rdr_after.readObject();
								JsonArray results_after = js_nested.getJsonArray("data");
								for (JsonObject result1 : results_after.getValuesAs(JsonObject.class)) {
									String writable = createWritable(result1);
									System.out.println(writable);
									bw.write(writable);
								}
							}
							bw.flush();
						}
					}
				} catch (Exception e) {
					System.out.println(e.getMessage());
				}
			}
			bw.close();
		}

	}
	
	

	public static void main(String[] args) throws Exception {
		fetchGroupComments("723281961067030", "Rawdata", "366376573541379|bOLAcwpD4do6E5ICztNP0ADp6xo");
	}

}
