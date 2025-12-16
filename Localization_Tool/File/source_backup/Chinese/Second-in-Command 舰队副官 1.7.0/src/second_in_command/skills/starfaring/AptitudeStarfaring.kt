package second_in_command.skills.starfaring

import com.fs.starfarer.api.campaign.CampaignFleetAPI
import com.fs.starfarer.api.campaign.econ.MarketAPI
import com.fs.starfarer.api.impl.campaign.ids.Factions
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import org.magiclib.kotlin.isPirateFaction
import second_in_command.SCData
import second_in_command.specs.SCAptitudeSection
import second_in_command.specs.SCBaseAptitudePlugin

class AptitudeStarfaring : SCBaseAptitudePlugin() {

    override fun addCodexDescription(tooltip: TooltipMakerAPI) {
        tooltip.addPara("星际航行 是本模组中最主要的后勤某组。它拥有许多在原版中属于工业天赋的技能。 " +
                "与另一种后勤能力 私掠海盗 相比，它更注重显著的实用性与便利性。 ",
            0f, Misc.getTextColor(), Misc.getHighlightColor(), "Starfaring", "Piracy")
    }

    override fun getOriginSkillId(): String {
        return "sc_starfaring_ad_astra"
    }

    override fun createSections() {

        var section1 = SCAptitudeSection(true, 0, "industry1")

        section1.addSkill("sc_starfaring_bulk_transport")
        section1.addSkill("sc_starfaring_salvaging")
        section1.addSkill("sc_starfaring_recovery_efforts")
        section1.addSkill("sc_starfaring_makeshift_equipment")
        //section1.addSkill("sc_starfaring_reactive_burn")
        addSection(section1)

        var section2 = SCAptitudeSection(true, 1, "industry2")
        section2.addSkill("sc_starfaring_navigation")
        section2.addSkill("sc_starfaring_starmapping")
        section2.addSkill("sc_starfaring_emergency_order")
        addSection(section2)

        var section3 = SCAptitudeSection(false, 3, "industry4")
        section3.addSkill("sc_starfaring_expedition")
        section3.addSkill("sc_starfaring_continuous_repairs")
        addSection(section3)


    }

    override fun getMarketSpawnweight(market: MarketAPI): Float {
        var weight = spec.spawnWeight
        if (market.faction.id == Factions.PIRATES) weight *= 0.75f
        else if (market.faction.isPirateFaction()) weight *= 0.80f
        return weight
    }

    override fun getNPCFleetSpawnWeight(data: SCData, fleet: CampaignFleetAPI)  : Float {
        return 0.33f
    }

}