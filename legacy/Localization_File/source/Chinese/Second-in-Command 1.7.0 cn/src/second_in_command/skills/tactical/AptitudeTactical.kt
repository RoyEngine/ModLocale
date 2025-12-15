package second_in_command.skills.tactical

import com.fs.starfarer.api.campaign.CampaignFleetAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCAptitudeSection
import second_in_command.specs.SCBaseAptitudePlugin

class AptitudeTactical : SCBaseAptitudePlugin() {

    override fun addCodexDescription(tooltip: TooltipMakerAPI) {
        tooltip.addPara("空间战术 是本模组中用途较广的天赋之一。 " +
                "虽然它本身并不十分突出，但常常可以使用它来完善自己的构筑。 ",
            0f, Misc.getTextColor(), Misc.getHighlightColor(), "空间战术", "")
    }

    override fun getOriginSkillId(): String {
        return "sc_tactical_focused_fire"
    }

    override fun createSections() {

        var section1 = SCAptitudeSection(true, 0, "combat1")
        section1.addSkill("sc_tactical_spotters")
        section1.addSkill("sc_tactical_rapid_response")
        section1.addSkill("sc_tactical_pristine_condition")
        section1.addSkill("sc_tactical_tactical_drills")
        section1.addSkill("sc_tactical_efficient_ordnance")
        //section1.addSkill("sc_tactical_superiority")
        addSection(section1)

        var section2 = SCAptitudeSection(true, 3, "combat2")
        section2.addSkill("sc_tactical_full_throttle")
        section2.addSkill("sc_tactical_accelerated_barrels")
        section2.addSkill("sc_tactical_mass_bombardment")
        section2.addSkill("sc_tactical_defensive_protocols")
        addSection(section2)


    }

    override fun getNPCFleetSpawnWeight(data: SCData, fleet: CampaignFleetAPI)  : Float {
        return 1f
    }



}