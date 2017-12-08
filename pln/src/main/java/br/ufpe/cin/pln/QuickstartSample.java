package br.ufpe.cin.pln;

import com.google.cloud.language.v1.AnalyzeSyntaxRequest;
import com.google.cloud.language.v1.AnalyzeSyntaxResponse;
//Imports the Google Cloud client library
import com.google.cloud.language.v1.Document;
import com.google.cloud.language.v1.Document.Type;
import com.google.cloud.language.v1.EncodingType;
import com.google.cloud.language.v1.LanguageServiceClient;
import com.google.cloud.language.v1.Token;

public class QuickstartSample {
	public static void main(String... args) throws Exception {
		try (LanguageServiceClient language = LanguageServiceClient.create()) {
		  Document doc = Document.newBuilder()
		      .setContent("Eu comi muito, mas não alcancei o ônibus.")
		      .setType(Type.PLAIN_TEXT)
		      .build();
		  
		  AnalyzeSyntaxRequest request = AnalyzeSyntaxRequest.newBuilder()
		      .setDocument(doc)
		      .setEncodingType(EncodingType.UTF16)
		      .build();
		  
		  // analyze the syntax in the given text
		  AnalyzeSyntaxResponse response = language.analyzeSyntax(request);
		  
		  // print the response
		  for (Token token : response.getTokensList()) {
		    System.out.printf("\tText: %s\n", token.getText().getContent());
		    System.out.printf("PartOfSpeechTag: %s\n", token.getPartOfSpeech().getTag());
		    System.out.println("DependencyEdge");
		    System.out.printf("\tHeadTokenIndex: %d\n", token.getDependencyEdge().getHeadTokenIndex());
		    System.out.printf("\tLabel: %s\n\n", token.getDependencyEdge().getLabel());
		  }
		}
	}
}
