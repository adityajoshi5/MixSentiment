package dataCollector;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.net.MalformedURLException;
import java.net.URL;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;

import javax.json.Json;
import javax.json.JsonArray;
import javax.json.JsonObject;
import javax.json.JsonReader;
import javax.json.JsonString;
import javax.json.JsonValue;

public class FacebookCommentExtractor {

	/**
	 * Take the Json object and extract the content we want to write into the
	 * file
	 */
	public static String createWritable(JsonObject myObj) {
		return myObj.getString("id") + "\t" + myObj.getJsonObject("from").getString("id") + "\t"
				+ myObj.getString("created_time") + "\t" + myObj.getString("message") + "\n";

	}

	public static boolean createFile(String path) throws IOException {
		File file = new File(path);
		long timestamp = System.currentTimeMillis();
		if (!file.exists()) {
			new FileOutputStream(file).close();
			return true; // indicating a new file was created
		}
		file.setLastModified(timestamp);
		return false;
	}

	public class CommentPagination {
		public ArrayList<String> comments;
		public String nextURL;
	}

	public class FBPostParsed {
		public String postCsv;
		public ArrayList<String> commentsCsvArray;
	}

	/**
	 * Read a Facebook API URL and return the top JSON object
	 */
	public static JsonObject readFacebookJson(URL url) throws IOException {
		System.setProperty("https.proxyHost", "proxy.iiit.ac.in");
		System.setProperty("https.proxyPort", "8080");
		InputStream is = url.openStream();
		JsonReader rdr = Json.createReader(is);
		return rdr.readObject();
	}

	public static String parseSingleComment(JsonObject comment) {
		String commentId = comment.getString("id");
		String userId = comment.getJsonObject("from").getString("id");
		String message = comment.getString("message");
		String created = comment.getString("created_time");
		String likes = String.valueOf(comment.getInt("like_count"));

		return commentId + "\t" + userId + "\t" + message.replace("\n", "").replace("\r", "") + "\t" + created + "\t"
				+ likes;
	}

	public static ArrayList<String> extractCommentsData(JsonArray commentData) {
		// Returns parsed comments + next link for pagination using a local
		// class
		ArrayList<String> comments = new ArrayList<String>();
		for (int i = 0; i < commentData.size(); i++) {
			comments.add(parseSingleComment((JsonObject) commentData.get(i)));
		}
		return comments;
	}

	public static String extractPostData(JsonObject thisPost) {
		String postId = thisPost.getString("id");
		String created = thisPost.getString("created_time");
		String shares;
		try {
			shares = thisPost.getJsonObject("shares").get("count").toString();
		} catch (Exception e) {
			shares = "0";
		}
		String message, picture;
		try {
			message = thisPost.getString("message").replace("\n", "[NL]").replace("\r", "[NL]");
			;
		} catch (Exception e) {
			message = "";
		}
		try {
			picture = thisPost.getString("picture");
		} catch (Exception e) {
			picture = "";
		}

		return postId + "\t" + created + "\t" + message + "\t" + picture + "\t" + shares;
	}

	public static String parseFBJson(JsonObject response, String postfile, String commentfile) throws IOException {

		JsonArray data = response.getJsonArray("data");
		JsonObject paging = response.getJsonObject("paging");
		String nextpage = paging.getString("next");

		for (int i = 0; i < data.size(); i++) {
			// Iterating over all the posts on the current page
			ArrayList<String> commentLines = new ArrayList<String>();
			JsonObject thisPost = (JsonObject) data.get(i);
			String thisPostId = thisPost.getString("id");
			String thisPostWritableData = extractPostData(thisPost);
			System.out.println(thisPostWritableData);
			JsonObject comments = thisPost.getJsonObject("comments");

			if (comments != null) { // handling 0 comment posts

				JsonArray commentData = comments.getJsonArray("data");
				JsonObject commentpaging = comments.getJsonObject("paging");
				JsonString nexturl = commentpaging.getJsonString("next");
				for (String com : extractCommentsData(commentData)) {
					commentLines.add(com + "\t" + thisPostId);
				}
				while (nexturl != null) {

					URL commenturl = new URL(nexturl.toString().substring(1, nexturl.toString().length() - 1)); // Generate
																												// next
																												// API
																												// call
					comments = readFacebookJson(commenturl);
					commentData = comments.getJsonArray("data");
					try {
						commentpaging = comments.getJsonObject("paging");
						nexturl = commentpaging.getJsonString("next");
					} catch (NullPointerException np) {
						nexturl = null;
					}
					for (String com : extractCommentsData(commentData)) {
						commentLines.add(com + "\t" + thisPostId);
					}
				} // Comment pagination ends
			} // Comment extraction section ends
			System.out.println(commentLines.size());

			BufferedWriter postwriter = new BufferedWriter(new FileWriter(postfile, true));
			BufferedWriter commentwriter = new BufferedWriter(new FileWriter(commentfile, true));
			postwriter.write(thisPostWritableData + "\t" + commentLines.size() + "\n");
			for (String comiter : commentLines) {
				commentwriter.write(comiter + "\n");
			}
			postwriter.close();
			commentwriter.close();

			if (i > 50) {
				break;
			} // Max pages to read
		} // Iterator over post ends

		return null;
	}

	public static void fetchCommentsToFile(String pageID, String token, String postfile, String commentfile)
			throws IOException {

		URL url = new URL("https://graph.facebook.com/" + pageID + "/posts?access_token=" + token);
		parseFBJson(readFacebookJson(url), postfile, commentfile);

	}
	
	public static ArrayList<String> getFileNames(String pagename, String extra){
		// Returns arraylist with two strings containing file name for post and comments
		ArrayList<String> names = new ArrayList<String>();
		pagename = pagename.replaceAll("[^a-zA-Z0-9]","");
		DateFormat dateFormat = new SimpleDateFormat("_MM_dd_HH_mm");
		Date date = new Date();
		names.add(("NewData/"+pagename+"_post"+dateFormat.format(date)+".txt"));
		names.add(("NewData/"+pagename+"_comment"+dateFormat.format(date)+".txt"));
		if (extra.length() > 0){
			System.out.println("NOT IMPL YET");
		}
		return names;
	}

	public static void main(String[] args) throws Exception {
		
		
		ArrayList<String> queuePages = new ArrayList<String>();
		
//		queuePages.add("logical.indian");
//		queuePages.add("narendramodi");
		queuePages.add("BeingSalmanKhan");
		queuePages.add("AamAadmiParty");
		queuePages.add("virat.kohli");
		queuePages.add("ComedyNightsWithKapil");
		
		
		for (String s : queuePages){
			System.out.println(s);
			ArrayList<String> outfiles = getFileNames(s, "");
			String postfile, commentfile;
			postfile=outfiles.get(0);
			commentfile=outfiles.get(1);
			System.out.println(postfile + " > " + commentfile);
			fetchCommentsToFile(s, "366376573541379|bOLAcwpD4do6E5ICztNP0ADp6xo",postfile, commentfile);
		}
		
		
	}
}
